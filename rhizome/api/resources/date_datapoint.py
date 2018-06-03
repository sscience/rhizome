
import logging
from tastypie import fields
from tastypie.resources import ALL
from pandas import DataFrame

from rhizome.api.serialize import CustomSerializer
from rhizome.api.resources.base_model import BaseModelResource
from rhizome.api.exceptions import RhizomeApiException
from rhizome.models.location_models import Location, LocationTree
from rhizome.models.document_models import Document, SourceSubmission
from rhizome.models.datapoint_models import DataPoint

from rhizome.api import custom_logic


class DateDatapointResource(BaseModelResource):
    '''
    - **GET Requests:**
        - *Required Parameters:*
            'indicator__in' A comma-separated list of indicator IDs to fetch. By default, all indicators
            'chart_type'
        - *Optional Parameters:*
            'location__in' A comma-separated list of location IDs
            'campaign_start' format: ``YYYY-MM-DD``  Include only datapoints from campaigns that began on or after the supplied date
            'campaign_end' format: ``YYYY-MM-DD``  Include only datapoints from campaigns that ended on or before the supplied date
            'campaign__in'   A comma-separated list of campaign IDs. Only datapoints attached to one of the listed campaigns will be returned
            'cumulative'
    '''

    indicator_id = fields.IntegerField(attribute='indicator_id', null=True)
    location_id = fields.IntegerField(attribute='location_id')

    class Meta(BaseModelResource.Meta):
        '''
        As this is a NON model resource, we must specify the object_class
        that will represent the data returned to the applicaton.  In this case
        as specified by the ResultObject the fields in our response will be
        location_id, campaign_id, indcator_json.
        The resource name is datapoint, which means this resource is accessed
        by /api/v1/datapoint/.
        The data is serialized by the CustomSerializer which uses the default
        handler for JSON responses and transforms the data to csv when the
        user clicks the "download data" button on the data explorer.
        note - authentication inherited from parent class


        # NOTE this needs to be cleaned up and any many of these methonds
        # should be executed by the parent ( base model resource )
        using the DataPoint as the object_class
        '''

        resource_name = 'date_datapoint'  # cooresponds to the URL of the resource
        GET_params_required = ['indicator__in']
        object_class = DataPoint
        required_fields_for_post = ['indicator_id','location_id', 'data_date', \
            'value']
        max_limit = None  # return all rows by default ( limit defaults to 20 )
        serializer = CustomSerializer()
        filtering = {
            'indicator_id' : ALL ,
            'location_id' : ALL ,
            'data_date' : ALL,
            'value'  : ALL
        }

    def __init__(self, *args, **kwargs):
        '''
        '''

        self.campaign_id_list, self.distinct_time_groupings = [],[]
        super(DateDatapointResource, self).__init__(*args, **kwargs)

    def add_default_post_params(self, bundle):
        '''
        This needs work.. perhaps we can create one submission
        per session, so that wer can trace back to what a user entered at
        a particular time.

        Right now all data entry every where will be associated with one id

        '''
        data_entry_doc_id = Document.objects.get(doc_title = 'Data Entry').id

        try:
            source_submission = SourceSubmission.objects.filter(document_id = \
                data_entry_doc_id)[0]
        except IndexError:
            source_submission = SourceSubmission.objects.create(document_id = \
                data_entry_doc_id, row_number = 0)

        bundle.data['source_submission_id'] = source_submission.id

        ## now put the unique index on the bundle ##
        unique_index = '{}-{}-{}'.format(bundle.data['location_id'],\
            bundle.data['indicator_id'], bundle.data['data_date'])
        bundle.data['unique_index'] = unique_index

        return bundle

    def get_response_meta(self, request, objects):

        meta = super(BaseModelResource, self)\
            .get_response_meta(request, objects)

        chart_uuid = request.GET.get('chart_uuid', None)
        if chart_uuid:
            meta['chart_uuid'] = chart_uuid

        ind_id_list = request.GET.get('indicator__in', '').split(',')
        meta['location_ids'] = [int(x) for x in self.location_ids]
        meta['indicator_ids'] = [int(x) for x in ind_id_list]
        meta['time_groupings'] = [x for x in self.distinct_time_groupings]

        return meta


    def apply_filters(self, request, applicable_filters):
        """
        """

        return self.get_object_list(request)

    def get_object_list(self, request):
        '''
        This is where the action happens in this resource.  AFter passing the
        url paremeters, get the list of locations based on the parameters passed
        in the url as well as the permissions granted to the user responsible
        for the request.
        Using the location_ids from the get_locations_to_return_from_url method
        we query the datapoint abstracted table, then iterate through these
        values cleaning the indicator_json based in the indicator_ids passed
        in the url parameters, and creating a ResultObject for each row in the
        response.
        '''

        self.time_gb = request.GET.get('group_by_time', None)
        self.start_date = request.GET.get('start_date', None) or \
            request.GET.get('campaign_start', None)
        self.end_date = request.GET.get('end_date', None) or \
            request.GET.get('campaign_end', None)
        self.location_id = request.GET.get('location_id', None)
        self.location_depth = 0 # FIXME on front end. request.GET.get('location_depth', 0)

        self.location_ids = None
        location_ids = request.GET.get('location_id__in', None)
        if location_ids:
            self.location_ids = location_ids.split(',')

        indicator__in = request.GET.get('indicator__in', None)
        if indicator__in:
            self.indicator__in = indicator__in.split(',')

        self.dp_df_columns = \
            ['data_date', 'indicator_id', 'location_id', 'value']

        group_by_param = request.GET.get('group_by_time', 'flat')
        if group_by_param == 'flat':
            self.location_ids = self.get_locations_to_return_from_url(request)
            qs = DataPoint.objects.filter(
                    location_id__in = self.location_ids,
                    indicator_id__in = self.indicator__in,
                    data_date__gte = self.start_date,
                    data_date__lte = self.end_date
                ).values(*self.dp_df_columns)
            return qs

        self.base_data_df = self.group_by_time_transform(request)

        ## if no datapoints, we return an empty list#
        if len(self.base_data_df) == 0:
            return []

        return self.base_data_df.to_dict('records')

    def get_time_group_series(self, dp_df):

        # if self.time_gb == 'year':
        #     dp_df['time_grouping'] = dp_df[
        #         'data_date'].map(lambda x: int(x.year))
        # elif self.time_gb == 'quarter':
        #     dp_df['time_grouping'] = dp_df['data_date']\
        #         .map(lambda x: str(x.year) + str((x.month - 1) // 3 + 1))
        # else:
        #     dp_df['time_grouping'] = dp_df['data_date']

        dp_df['time_grouping'] = dp_df['data_date']

        ## find the unique possible groupings for this time range and gb param
        ## FIXME -- this wont work for quarter groupingings, only years.
        self.distinct_time_groupings = list(dp_df.time_grouping.unique())
        if not self.distinct_time_groupings:
            start_yr, end_yr = self.start_date[0:4],\
                self.end_date[0:4]
            self.distinct_time_groupings = range(int(start_yr), int(end_yr))

        return dp_df

    def handle_discrete_location_request(self):

        discret_loc_dp_df_cols = self.dp_df_columns
        discret_loc_dp_df_cols.append('id')

        dp_df = DataFrame(list(DataPoint.objects.filter(
                location_id__in = self.location_ids,
                indicator_id__in = self.indicator__in,
                data_date__gte = self.start_date,
                data_date__lte = self.end_date
            ).values(*discret_loc_dp_df_cols)), columns=self.dp_df_columns)

        return dp_df


    def group_by_time_transform(self, request):
        '''
            Imagine the following location tree heirarchy
            ( Country -> Region -> Province -> District )

            Based on these two queries return the coorseponding result
                1. Show Polio cases in Afghanistan with a bubble on each
                    province
                2. Show Polio cases in Afghanistan with a bubble on each
                    district
                2. Show Polio cases in the southern Region with a bubble
                    on each district
        '''

        logging.warning('[group_by_time_transform] - location_id %s',
            self.location_id)
        logging.warning('[group_by_time_transform] - location_depth %s',
            self.location_depth)

        if self.location_ids:
            return self.handle_discrete_location_request()

        else:
            loc_tree_df_columns = ['parent_location_id','location_id']
            self.location_ids = LocationTree.objects.filter(
                parent_location_id = self.location_id,
                lvl = self.location_depth
            ).values_list('location_id', flat=True)

            print '===--==='
            print self.location_ids
            print '===--==='
            # ## this is a hack to deal with this ticket ##
            # # https://trello.com/c/No82UpGl
            if len(self.location_ids) == 0:
                self.location_ids = Location.objects.filter(
                    parent_location_id=self.location_id,
                ).values_list('id', flat=True)

            loc_tree_df = DataFrame(list(LocationTree.objects.filter(
                parent_location_id = self.location_ids,
            ).values_list(*loc_tree_df_columns)),columns = loc_tree_df_columns)

            print '===-loc_tree_df-==='
            print loc_tree_df
            print '===-loc_tree_df-==='

            dp_loc_ids = [self.location_id]
            if self.location_depth > 0:
                    dp_loc_ids = list(loc_tree_df['location_id'].unique())

            dp_df = DataFrame(list(DataPoint.objects.filter(
                    # location_id__in = dp_loc_ids,
                    indicator_id__in = self.indicator__in,
                    data_date__gte = self.start_date,
                    data_date__lte = self.end_date
                ).values(*self.dp_df_columns)), columns=self.dp_df_columns)

        if len(dp_df) == 0:
            return []

        time_grouped_dp_df = self.get_time_group_series(dp_df)

        # print '====time_grouped_dp_df==='
        # print time_grouped_dp_df[:3]
        # print '====loc_tree_df==='
        # print loc_tree_df[:3]

        merged_df = time_grouped_dp_df.merge(loc_tree_df)

        # print '====merged_df==='
        # print merged_df[:3]

        ## sum all values for locations with the same parent location
        gb_df = DataFrame(merged_df
              .groupby(['indicator_id', 'time_grouping', 'parent_location_id'])['value']
              .sum())\
              .reset_index()

        print '=gb_df'
        print gb_df[:3]

        gb_df = gb_df.rename(columns={
            'parent_location_id': 'location_id',
            })

        gb_df = gb_df.rename(columns={'parent_location_id': 'location_id'})

        print '==-gb_df -=='
        print gb_df[:2]

        # gb_df = gb_df.sort(['time_grouping'], ascending=[1])

        return gb_df
