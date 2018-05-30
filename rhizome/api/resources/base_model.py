import json

from django.db import IntegrityError
from django.core.exceptions import (
    ObjectDoesNotExist, MultipleObjectsReturned
)

from jsonfield import JSONField
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication, MultiAuthentication
from tastypie.resources import ModelResource, ALL
from tastypie import http

from rhizome.api.serialize import CustomSerializer
from rhizome.api.custom_session_authentication import\
    CustomSessionAuthentication
from rhizome.api.custom_cache import CustomCache
from rhizome.api.resources.base_resource import BaseResource
from rhizome.api.exceptions import RhizomeApiException

from rhizome.models.location_models import Location, LocationTree, \
    LocationType


class BaseModelResource(ModelResource, BaseResource):
    '''
    This applies to only the V1 API.  This method inherits from Tastypie's
    model resource.

    This resource strips down almost all of the tastypie functions which
    drastically slow down the API performance.

    IMPORTANT: if you note, all of the resources use the .values() option for
    each queryset.  That returns the model as JSON, so the idea is that the
    API does not need to serialize or dehydrate the resource.

    The models are set up so that the API does as little transformation as
    possible.  That means however, that a few of our metadata models ( see
    campaign / indicator ) are cached and contain related information making
    the job of the API easy.
    '''

    class Meta:
        # authentication = MultiAuthentication(
        #     CustomSessionAuthentication(), ApiKeyAuthentication())
        # authorization = Authorization()
        always_return_data = True
        allowed_methods = ['get', 'post', 'delete', 'patch']
        cache = CustomCache()
        serializer = CustomSerializer()
        filtering = {
            "id": ALL,
        }
        GET_params_required = []

    def obj_get(self, bundle, **kwargs):
        """
        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.

        Currently used to find one object from the url api/v1/resource/<pk>/

        Try to find an object using the pk
        """

        try:
            obj = self._meta.object_class.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            msg = 'No {0} object found for id : {1}'\
                .format(self._meta.resource_name, kwargs['pk'])
            raise RhizomeApiException(message=msg, code=500)
        except MultipleObjectsReturned:
            raise http.HttpMultipleChoices("More than one resource found\
                at this URI.")

        return obj

    def get_detail(self, request, **kwargs):
        """
        Returns a single serialized resource.
        Calls ``cached_obj_get/obj_get`` to provide the data, then handles
        that result set and serializes it.
        Should return a HttpResponse (200 OK).

        In this case, if the bundle gives us a message ( and a code ) we raise
        an exception.  This is to handle the case that the object does not
        exist.
        """

        obj = self.obj_get(None, **kwargs)
        bundle = self.build_bundle(obj=obj, request=request)
        bundle.data = obj.__dict__

        bundle.data.pop('_state')

        return self.create_response(request, bundle)

    def get_object_list(self, request):
        """
        An ORM-specific implementation of ``get_object_list``.
        Returns a queryset that may have been limited by other overrides.
        """

        try:
            query_felds = self._meta.GET_fields
            qs = self._meta.object_class.objects.all().values(*query_felds)
        except AttributeError:
            qs = self._meta.object_class.objects.all().values()

        return qs

    def apply_filters(self, request, applicable_filters):
        """
        An ORM-specific implementation of ``apply_filters``.
        The default simply applies the ``applicable_filters`` as ``**kwargs``,
        but should make it possible to do more advanced things.
        """
        return self.get_object_list(request).filter(**applicable_filters)

    def obj_get_list(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_get_list``.
        ``GET`` dictionary of bundle.request can be used to narrow the query.
        """

        ## validate the filters ##
        filters = self.validate_filters(bundle.request)

        ## Update with the provided kwargs ##
        filters.update(kwargs)

        ## clean and prepare the filters and their relavant query terms ##
        applicable_filters = self.build_filters(filters=filters)

        ## get the objects and apply the filters ##
        objects = self.apply_filters(bundle.request, applicable_filters)

        return objects

    def get_list(self, request, **kwargs):
        """
        Overriden from Tastypie..
        """

        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(
            bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        bundles = []

        if len(objects) > 0:
            # find json_fields ( should be explicit here and check data type )
            # i.e. find the field datatypes from the model definition
            json_obj_keys = [k for k, v in objects[0].items() if 'json' in k]

        for obj in objects:

            # serialize json fields ##
            for json_key in json_obj_keys:
                obj[json_key] = json.loads(obj[json_key])

            # hack lvl attribute FIXME
            if 'location_type_id' in obj:
                obj['lvl'] = obj['location_type_id'] - 1

            bundles.append(obj)

        response_meta = self.get_response_meta(request, bundles)

        response_data = {
            'objects': bundles,
            'meta': response_meta,  # add paginator info here..
            'error': None,
        }

        return self.create_response(request, response_data)

    def post_list(self, request, **kwargs):
        """
        Creates a new resource/object with the provided data.
        Calls ``obj_create`` with the provided data and returns a response
        with the new resource's location.
        If a new resource is created, return ``HttpCreated`` (201 Created).
        If ``Meta.always_return_data = True``, there will be a populated body
        of serialized data.

        I think this code can all be removed except for --

            bundle = self.build_bundle(data=deserialized, request=request)

            updated_bundle = self\
                .obj_create(bundle, **self.remove_api_resource_names(kwargs))
        """

        deserialized = self.deserialize(
            request,
            request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json')
        )
        deserialized = self\
            .alter_deserialized_detail_data(request, deserialized)

        bundle = self.build_bundle(data=deserialized, request=request)

        updated_bundle = self\
            .obj_create(bundle, **self.remove_api_resource_names(kwargs))

        location = self.get_resource_uri(updated_bundle)

        return self.create_response(request, updated_bundle,
                                    response_class=http.HttpCreated, location=location)

    def update_object(self, obj, **kwargs):
        """
        """

        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.save()

        return obj

    def add_default_post_params(self, bundle):
        '''
        by default do nothing, but this method allows for us to add any
        information ( say for instance user id ) to the data that we
        POST.
        '''
        return bundle

    def obj_create(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.

        This also handles updates ( PUT ) requests by looking if the
        request has the ID in there, and if so, updating the resorce with the
        relevant data items.
        """

        # add any additional data needed for post, for instance datapoitns
        # that are inserted via a POST request should have a document
        bundle = self.add_default_post_params(bundle, **kwargs)

        ## Try to validate / clean the POST before submitting the INSERT ##
        bundle = self.validate_obj_create(bundle, **kwargs)

        #### FIXME REMOVE BELOW CODE AND USE PROPER PATCH FORMAT ####
        id_from_post = bundle.data.get('id', None)
        if id_from_post == '-1':
            del bundle.data['id']
            id_from_post = None

        if id_from_post:  # this is a PUT or update of an existing resource #
            obj = self._meta.object_class.objects.get(id=id_from_post)
            self.update_object(obj, **bundle.data)
        #### REMOVE ABOVE CODE ####

        else:  # create the object with the data from the request #
            try:
                obj = self._meta.object_class.objects.create(**bundle.data)
            except IntegrityError as err:
                raise RhizomeApiException(message=err.message, code=497)

        bundle.obj = obj
        bundle.data['id'] = bundle.obj.id

        return bundle

    def validate_obj_create(self, bundle, **kwargs):
        '''
        Custom module that is meant to clean and check the POST request, making
        sure that we catch any errors we can befoer submitting to the database.

        For instance, here, we check that the necessary Keys are there, so that
        we can save a trip to the DB by using the `required_fields_for_post`
        attribute on the Meta class of the base_model resoruce.
        '''

        keys_passed = [unicode(x) for x in bundle.data.keys()]
        keys_req = [unicode(x) for x in self._meta.required_fields_for_post]
        missing_keys = set(keys_req).difference(set(keys_passed))

        if len(missing_keys) > 0:
            raise RhizomeApiException(message='missing params %s' %
                                      missing_keys)

        bundle = self.clean_json_fields(bundle)

        return bundle

    def clean_json_fields(self, bundle):
        '''
        For the models in which we store JSON data namely  ( custom_chart,
        custom_dashboard ) serialize the json and upaate the bundle in place.
        '''

        for f in self._meta.object_class._meta.fields:
            ## if the field is a json data tyep and it exists in the bundle ##
            if isinstance(f, JSONField) and bundle.data.has_key(f.name):
                bundle.data[f.name] = json.loads(bundle.data[f.name])

        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        """
        """

        obj = self.obj_get(bundle=bundle, **kwargs)
        db_obj = self._meta.object_class.objects.get(id=obj.id)
        updated_obj = self.update_object(db_obj, **bundle.data)
        bundle.obj = updated_obj

    ### DELETE ###

    def obj_delete(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.
        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.

        To Do -- Check 'is_superuser' flag
        """

        obj = self.obj_get(bundle=bundle, **kwargs)
        obj = self._meta.object_class.objects.get(id=obj.id).delete()

    def obj_delete_list(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete_list``.
        """
        return super(BaseResource, self)\
            .obj_delete_list(bundle, **kwargs)

    def get_locations_to_return_from_url(self, request):
        '''
        This method is used in both the /geo and /datapoint endpoints.  Based
        on the values parsed from the URL parameters find the locations needed
        to fulfill the request based on the four rules below.

        TO DO -- Check Location Permission so that the user can only see
        What they are permissioned to.
        '''

        # if location_id__in requested.. we return exactly those ids
        # for instance if you were doing data entry for 5 specific districts
        # you would use the location_id__in param to fetch just those ids

        self.location_id = request.GET.get('location_id', None)
        self.location_id_list = request.GET.get('location_id__in', None)
        self.location_type = request.GET.get('location_type', None)
        self.location_depth = request.GET.get('location_depth', 0)

        ## fixme -- this is a hack due to the fact that we have different location types set up in BE / FE
        if self.location_depth == '':
            self.location_depth = 1

        self.location_depth = int(self.location_depth)

        if self.location_id_list:
            location_ids = self.location_id_list.split(',')

        elif self.location_id:

            # woul be nice to put the location_type as a string for each
            # row in the locatino tree table that we don't have to
            # make these three queries

            if self.location_type:  # figure out the depth level #
                parent_location_location_type_id = Location.objects.\
                    get(id=self.location_id).location_type_id

                parent_location_admin_level = LocationType.objects.\
                    get(id=parent_location_location_type_id).admin_level

                location_type_location_admin_level = LocationType.objects.\
                    get(name=self.location_type).admin_level

                self.location_depth = location_type_location_admin_level - \
                    parent_location_admin_level

            location_ids = LocationTree.objects.filter(
                parent_location_id=self.location_id,
                lvl=self.location_depth
            ).values_list('location_id', flat=True)

            ## this is a hack to deal with this ticket ##
            # https://trello.com/c/No82UpGl
            # this says -- if there are no data at this locatin level
            # we just find district level data ..  use case - i want districts
            # at afghanistan, and south, and kandahar.
            if len(location_ids) == 0:
                district_location_type_id = LocationType.objects\
                    .get(name='District').id
                location_ids = LocationTree.objects.filter(
                    parent_location_id=self.location_id,
                    location__location_type_id=district_location_type_id
                ).values_list('location_id', flat=True)

        else:
            # this really shouldn't happen -- when this condition hits
            # the app slows down.  Need to enforce on the FE that we
            # pass a `location_id` and also when possible a `depth_level`
            location_ids = Location.objects.all().values_list('id', flat=True)
            # raise RhizomeApiException\
            #     ('Please pass either `location_id__in` to get specific\
            #     locations, or both `location_id and `location_depth` for a\
            #     recursive result')


        return location_ids

    # def get_locations_from_filter_param(self, location_ids,
    #                                     indicator_to_filter, value_to_filter):
    #     '''
    #     futher filter locations that have the indicator / value filter
    #     in the computed datapoint table.
    #
    #     This is where for instance, we would take care of the filter that says
    #     "we only want to see polio cases in `access challenged` areas."
    #
    #     so the query would come in as
    #     {filter_indicator: <is_access_challenged>, filter_value<True>}
    #
    #     and return only locations that meet that condition.
    #     '''
    #
    #     location_ids = DataPointComputed.objects.filter(
    #         campaign__in=self.campaign_id_list,
    #         location__in=location_ids,
    #         indicator__short_name=indicator_to_filter,
    #         value__in=value_to_filter.split(','))\
    #         .values_list('location_id', flat=True)
    #
    #     return location_ids
