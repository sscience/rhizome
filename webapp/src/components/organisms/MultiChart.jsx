import _ from 'lodash'
import React, {PropTypes} from 'react'
import Reflux from 'reflux'
import moment from 'moment'

import PalettePicker from 'components/organisms/data-explorer/preview/PalettePicker'
import ChartSelect from 'components/organisms/data-explorer/ChartSelect'

import builderDefinitions from 'components/molecules/charts/utils/builderDefinitions'
import CampaignSelector from 'components/molecules/CampaignSelector'
import IndicatorSelector from 'components/molecules/IndicatorSelector'
import LocationSelector from 'components/molecules/LocationSelector'
import DatabrowserTable from 'components/molecules/DatabrowserTable'
import DateRangePicker from 'components/molecules/DateRangePicker'
import Placeholder from 'components/molecules/Placeholder'
import TitleInput from 'components/molecules/TitleInput'
import TableChart from 'components/molecules/charts/TableChart'
import LineChart from 'components/molecules/charts/LineChart'
import ChoroplethMap from 'components/molecules/charts/ChoroplethMap'

import LocationStore from 'stores/LocationStore'
import IndicatorStore from 'stores/IndicatorStore'
import CampaignStore from 'stores/CampaignStore'
import RootStore from 'stores/RootStore'

const MultiChart = React.createClass({
  mixins: [
    Reflux.connect(LocationStore, 'locations'),
    Reflux.connect(CampaignStore, 'campaigns'),
    Reflux.connect(IndicatorStore, 'indicators')
  ],

  getInitialState () {
    console.info('MultiChart.getInitialState')
    return {
      titleEditMode: false
    }
  },

  componentDidMount () {
    console.info('MultiChart.componentDidMount')
    RootStore.listen(() => {
      const state = this.state
      if (state.locations.index && state.indicators.index && state.campaigns.index && state.charts.index) {
        if (this.props.chart_id) {
          this.props.fetchChart.completed(this.state.charts.index[this.props.chart_id])
        } else {
          this.props.setIndicators(this.state.indicators.index[27])
          this.props.setLocations(this.state.locations.index[1])
          this.props.setCampaigns(this.state.campaigns.raw[0])
        }
      }
    })
    if (this.props.chart_id) { this.setState({footerHidden: true}) }
  },

  shouldComponentUpdate (nextProps, nextState) {
    const missing_params = _.isEmpty(nextProps.chart.selected_indicators) || _.isEmpty(nextProps.chart.selected_locations)
    const chart_data = !_.isEmpty(nextProps.chart.data)
    return chart_data || nextProps.chart.loading || missing_params
  },

  _toggleTitleEdit (title) {
    if (_.isString(title)) {
      this.props.setTitle(title)
    }
    this.setState({titleEditMode: !this.state.titleEditMode})
  },

  getChartComponentByType (type) {
    if (type === 'TableChart') {
      return <TableChart {...this.props.chart} />
    } else if (type === 'LineChart') {
      return <LineChart {...this.props.chart} />
    } else if (type === 'ChoroplethMap') {
      return <ChoroplethMap {...this.props.chart} />
    }
  },

  render () {
    console.info('MultiChart.RENDER ==========================================')
    const chart = this.props.chart
    const start_date = chart ? moment(chart.start_date, 'YYYY-MM-DD').toDate() : moment()
    const end_date = chart ? moment(chart.end_date, 'YYYY-MM-DD').toDate() : moment()
    const disableSave = _.isEmpty(chart.selected_locations) || _.isEmpty(chart.selected_indicators)
    const multi_indicator = chart.type === 'TableChart' || chart.type === 'RawData'
    const multi_location = chart.type === 'TableChart' || chart.type === 'RawData'

    // CHART
    // ---------------------------------------------------------------------------
    const title_bar = this.state.titleEditMode ?
      <TitleInput initialText={chart.title} save={this._toggleTitleEdit}/>
      :
      <h1>
        {chart.title}
        <a className='button icon-button' onClick={this._toggleTitleEdit}><i className='fa fa-pencil'/></a>
        <br/ >
        <small>{chart.uuid}</small>
      </h1>

    const chart_component = chart.type === 'RawData'?
      <DatabrowserTable
        data={chart.data}
        selected_locations={chart.selected_locations}
        selected_indicators={chart.selected_indicators}
      />
      : this.getChartComponentByType(chart.type)

    // SIDEBAR
    // ---------------------------------------------------------------------------
    const date_range_picker = chart.type === 'LineChart' || chart.type === 'TableChart' ? (
      <div className='medium-12 columns'>
        <h3>Time</h3>
        <DateRangePicker
          sendValue={this.props.setDateRange}
          start={start_date}
          end={end_date}
          fromComponent='MultiChart'
        />
        <br/>
      </div>
    ) : null

    const campaign_selector = chart.type !== 'LineChart' ? (
      <CampaignSelector
        campaigns={this.state.campaigns}
        selected_campaigns={chart.selected_campaigns}
        selectCampaign={this.props.selectCampaign}
        deselectCampaign={this.props.deselectCampaign}
        setCampaigns={this.props.setCampaigns}
        classes='medium-12 columns'
      />
    ) : ''

    const location_selector = (
      <LocationSelector
        locations={this.state.locations}
        selected_locations={chart.selected_locations}
        selectLocation={this.props.selectLocation}
        deselectLocation={this.props.deselectLocation}
        setLocations={this.props.setLocations}
        clearSelectedLocations={this.props.clearSelectedLocations}
        classes={multi_location ? 'medium-6 columns' : 'medium-12 columns'}
        multi={multi_location}
      />
    )

    const indicator_selector = (
      <IndicatorSelector
        indicators={this.state.indicators}
        selected_indicators={chart.selected_indicators}
        selectIndicator={this.props.selectIndicator}
        setIndicators={this.props.setIndicators}
        deselectIndicator={this.props.deselectIndicator}
        clearSelectedIndicators={this.props.clearSelectedIndicators}
        reorderIndicator={this.props.reorderIndicator}
        classes={multi_indicator ? 'medium-6 columns' : 'medium-12 columns'}
        multi={multi_indicator}
      />
    )

    const chart_type_selector = (
      <div className='medium-7 columns'>
        <h3>View</h3>
        <ChartSelect
          charts={builderDefinitions.charts}
          value={chart.type}
          onChange={this.props.setType}/>
      </div>
    )
    const palette_selector = (
      <div className='medium-5 columns'>
        <h3>Color Scheme</h3>
        <PalettePicker
          value={chart.palette}
          onChange={this.props.setPalette}/>
      </div>
    )
    const remove_chart_button = this.props.removeChart ? (
      <button className='button icon-button right remove-chart-button' onClick={() => this.props.removeChart(chart.uuid)}>
        <i className='fa fa-times-circle fa-2x'/>
      </button>
    ) : ''

    // PLACEHOLDERS
    // ---------------------------------------------------------------------------
    const missingParams = _.isEmpty(chart.selected_indicators) || _.isEmpty(chart.selected_locations)
    let chart_placeholder = <Placeholder height={400}/>
    if (!chart.loading && missingParams) {
      chart_placeholder = <Placeholder height={400} text='Please select an INDICATOR and LOCATION' loading={false}/>
    } else if (_.isEmpty(chart.data) && !_.isNull(chart.data) && chart.loading) {
      chart_placeholder = <Placeholder height={400} text='NO DATA' loading={false}/>
    }

    return (
      <section className='multi-chart row'>
        <div className='medium-4 large-2 medium-push-8 large-push-10 columns'>
          { remove_chart_button }
          { date_range_picker }
          { campaign_selector }
          { indicator_selector }
          { location_selector }
        </div>
        <div className='medium-8 large-10 medium-pull-4 large-pull-2 columns'>
          <div className='row chart-header text-center'>
            { title_bar }
          </div>
          {!_.isEmpty(chart.data) ? chart_component : chart_placeholder}
        </div>
      </section>
    )
  }
})

export default MultiChart
