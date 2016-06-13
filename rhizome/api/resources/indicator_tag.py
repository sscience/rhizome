from tastypie.resources import ALL

from rhizome.api.resources.base_model import BaseModelResource
from rhizome.models import IndicatorTag


class IndicatorTagResource(BaseModelResource):
    '''
    **GET Request** Returns all indicator tags
        - *Optional Parameters:*
            'show_leaf'only return leaf level nodes of the indicator_tag tree
            'id' return the indicator_tag associated with the given id
        - *Errors:*

    **POST Request** Creates an indicator tag
        - *Required Parameters:*
            'tag_name'
        - *Optional Parameters:*
            'parent_tag_id'
        - *Errors:*
            if a required parameter is not supplied, the API will return a 500 error
    '''

    class Meta(BaseModelResource.Meta):
        GET_fields = ['id', 'parent_tag_id', 'tag_name', 'parent_tag__tag_name']
        object_class = IndicatorTag
        resource_name = 'indicator_tag'
        filtering = {
            'id': ALL,
            'tag_name': ALL,
            'parent_tag_id':ALL
        }
        required_fields_for_post = ['tag_name']

    def get_object_list(self, request):
        '''
        The 'show_leaf' parameter only shows the leaf level nodes of the tree

        Also, the ID param will filter the results to the tag id requested

        Note -- getting the tag by ID should be changed to use a REST style
        endpoint like so : api/v1/indicator_tag/<id>/

        '''

        try:
            request.GET['show_leaf']
            all_parents = list(set(IndicatorTag.objects
                                   .filter(parent_tag_id__gt=0)
                                   .values_list('parent_tag_id', flat=True)))
            return IndicatorTag.objects.exclude(id__in=all_parents).values()
        except KeyError:
            pass

        try:
            tag_id = request.GET['id']
            return IndicatorTag.objects.filter(id=tag_id).values()
        except KeyError:
            return super(IndicatorTagResource, self).get_object_list(request)
