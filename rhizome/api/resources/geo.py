import json

from rhizome.models.location_models import MinGeo, Location, LocationTree, \
    LocationType
from rhizome.api.resources.base_non_model import BaseNonModelResource
from tastypie import fields
from tastypie.resources import ALL

class GeoJsonResult(object):
    location_id = int()
    type = unicode()
    properties = dict()
    geometry = dict()
    parent_location_id = int()


class GeoResource(BaseNonModelResource):
    '''
    A non model resource that allows us to query for shapefiles based on a
    colletion of parameters.
    '''

    location_id = fields.IntegerField(attribute='location_id')
    type = fields.CharField(attribute='type')
    properties = fields.DictField(attribute='properties')
    geometry = fields.DictField(attribute='geometry')
    parent_location_id = fields.IntegerField(attribute='parent_location_id')

    class Meta(BaseNonModelResource.Meta):
        object_class = GeoJsonResult
        resource_name = 'geo'
        filtering = {
            "location_id": ALL,
        }

    def get_object_list(self, request):
        '''
        parse the url, query the polygons table and do some
        ugly data munging to convert the results from the DB into geojson
        '''
        features = []

        location_ids_to_return = self.get_locations_to_return_from_url(request)

        location_ids = Location.objects\
            .filter(id__in = location_ids_to_return)\
            .values_list('id', flat =True)

        polygon_values_list = MinGeo.objects.filter(location_id__in=\
            location_ids)

        for p in polygon_values_list:
            geo_obj = GeoJsonResult()
            geo_obj.location_id = p.location.id

            try:
                geo_obj.geometry = p.geo_json['geometry']
            except KeyError:
                geo_obj.geometry = p.geo_json ## p.geo_json['coordinates']
        #
        #     print '==--==\n' * 5
        #     print p
        #     print '==--==\n' * 5
        #
        #     # geo_obj.type = p.geo_json['type']
        #     geo_obj.properties = {'location_id': p.location.id}
        #     geo_obj.parent_location_id =\
        #         p.location.id if p.location.parent_location_id is None else p.location.parent_location_id
            features.append(geo_obj.__dict__)
        return features

    def obj_get_list(self, bundle, **kwargs):
        '''
        Outer method for get_object_list... this calls get_object_list and
        could be a point at which additional build_agg_rc_dfing may be applied
        '''
        return self.get_object_list(bundle.request)

    def dehydrate(self, bundle):

        bundle.data.pop("resource_uri", None)
        return bundle

    def alter_list_data_to_serialize(self, request, data):
        '''
        If there is an error for this resource, add that to the response.  If
        there is no error, than add this key, but set the value to null.  Also
        add the total_count to the meta object as well
        '''
        # get rid of the meta_dict. i will add my own meta data.
        data['type'] = "FeatureCollection"
        data['features'] = data['objects']
        data['error'] = None ## fix this.

        data.pop("objects", None)
        data.pop("meta", None)

        if 'parent_location_id__in' in request.GET:
            data['parent_location_id__in'] = request.GET['parent_location_id__in']
        elif 'location_id__in' in request.GET:
            data['location_id__in'] = request.GET['location_id__in']


        return data

    # FIXME - this is duped. make geo a BaseModelResource and remove below code
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
