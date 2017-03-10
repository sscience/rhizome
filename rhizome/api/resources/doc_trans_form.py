from rhizome.api.resources.base_non_model import BaseNonModelResource
from rhizome.models.document_models import Document, SourceSubmission
from rhizome.models.datapoint_models import DataPoint

class DocTransFormResource(BaseNonModelResource):
    '''
    **GET Request** Runs document transform, refresh master, and agg refresh
        for a given document
        - *Required Parameters:*
            'document_id'
        - *Errors:*
            returns 500 error if no document id is provided
    '''

    class Meta(BaseNonModelResource.Meta):
        '''
        '''
        resource_name = 'transform_upload'
        queryset = SourceSubmission.objects.all().values()
        GET_params_required = ['document_id']

    def pre_process_data(self, request):
        '''
        ## when you upload a file, step one is getting data into source
            submission
            ## --> DocTransform <-- ##
        ## Step two is translating form source_submission into datapoints
            ## --> REfreshMaster <----
        ## step three is aggregation
            ## agg refresh ##
        '''

        document_object = Document.objects\
            .get(id = request.GET.get('document_id'))

        document_object.transform_upload()
        document_object.refresh_master()

        return Document.objects.filter(id=document_object.id).values()
