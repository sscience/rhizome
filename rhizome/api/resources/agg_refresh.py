from rhizome.api.resources.base_non_model import BaseNonModelResource
from rhizome.api.exceptions import RhizomeApiException


# FIXME -- REMOVE THIS 

class AggRefreshResource(BaseNonModelResource):
    '''
        **GET Request** Runs agg_refresh on the backend
          - *Optional Parameters:*
              'id': campaign id of the campaign to run agg refresh on.
              If the parameter is not set, the API will run agg refresh on a
              randomly chosen campaign that needs to be aggregated.
          - *Errors:*
              if an invalid id is provided, the API returns a 500 error
    '''

    class Meta(BaseNonModelResource.Meta):
        resource_name = 'agg_refresh'
        GET_params_required = ['campaign_id']

    def get_object_list(self, request):
        '''
        After runnign the agg refresh, return the campaign data to the broweser
        '''

        campaign_id = request.GET.get('campaign_id')

        return []
