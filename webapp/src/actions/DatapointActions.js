import Reflux from 'reflux'
import api from 'utilities/api'

const DatapointActions = Reflux.createActions({
  'fetchDatapoints': { children: ['completed', 'failed'], asyncResult: true },
  'clearDatapoints': 'clearDatapoints'
})

// API CALLS
// ---------------------------------------------------------------------------
DatapointActions.fetchDatapoints.listen(params => {
  const query = _prepDatapointsQuery(params)
  // const namespace = params['group_by_time'] === 'campaign' ? '/campaign_datapoint/' : '/date_datapoint/'
  const namespace = '/date_datapoint/' // lebanon instance dosnt use campaign
  const fetch = api.endPoint(namespace)
  DatapointActions.fetchDatapoints.promise(
    fetch(query, null, )
  )
})

// ACTION HELPERS
// ---------------------------------------------------------------------------
const _prepDatapointsQuery = (params) => {
  // const chartNeedsNullData = _.indexOf(builderDefinitions.need_missing_data_charts, params.type) !== -1
  let query = {
    campaign__in: params.campaign__in || params.campaign_ids,
    indicator__in: params.indicator_ids.join(),
    chart_uuid: params.uuid,
    group_by_time: params.group_by_time,
    filter_indicator: params.indicator_filter ? params.indicator_filter.type : null,
    filter_value: params.indicator_filter ? params.indicator_filter.value : null
  }
  if (params.type === 'RawData' && params.group_by_time !== 'year') {
    query.start_date = params.start_date
    query.end_date = params.end_date
    query.location_id__in = params.location_ids.join()
  } else {
    // clean this up... we need ability to select discrete locations in the chart builder.
    // currently, we will only allow for a single location and a "depth" param in the chart builder
    query.campaign_start = params.start_date
    query.campaign_end = params.end_date
    query.location_depth = params.location_depth <= 0 ? null : params.location_depth
    query.location_id = params.location_ids[0]
  }

  return query
}

export default DatapointActions
