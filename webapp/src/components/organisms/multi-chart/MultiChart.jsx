import _ from 'lodash'
import React from 'react'
import Reflux from 'reflux'

import DatapointTable from 'components/table/DatapointTable'
import ChartTypeSelect from 'components/select/ChartTypeSelect'
import ChartSelect from 'components/select/ChartSelect'
import Placeholder from 'components/Placeholder'

import BarChart from 'components/highchart/BarChart'
import MapChart from 'components/highchart/MapChart'
import BubbleMapChart from 'components/highchart/BubbleMapChart'
import LineChart from 'components/highchart/LineChart'
import ColumnChart from 'components/highchart/ColumnChart'

import MultiChartControls from 'components/organisms/multi-chart/MultiChartControls'
import MultiChartHeader from 'components/organisms/multi-chart/MultiChartHeader'

import ChartStore from 'stores/ChartStore'
import CampaignStore from 'stores/CampaignStore'
import RootStore from 'stores/RootStore'

const MultiChart = React.createClass({

  mixins: [
    Reflux.connect(ChartStore, 'all_charts'),
    Reflux.connect(CampaignStore, 'campaigns'),
  ],

  componentDidMount: function () {
    RootStore.listen(() => {
      if (this.props.chart_id) {
        this.props.fetchChart.completed(this.state.charts.index[this.props.chart_id])
      } else {
        this.props.setCampaigns(this.state.campaigns.raw[0])
      }
    })
  },

  shouldComponentUpdate: function (nextProps, nextState) {
    const missing_params = _.isEmpty(nextProps.chart.selected_indicators) || _.isEmpty(nextProps.chart.selected_locations)
    const chart_data = !_.isEmpty(nextProps.chart.data)
    const chart_data_changed  = nextProps.chart.loading !== this.props.chart.loading
    return chart_data || nextProps.chart.loading || missing_params || chart_data_changed
  },

  getChartComponentByType: function (type) {
    // if (type === 'TableChart') {
    //   return <TableChart {...this.props.chart} />
    // } else
    if (type === 'LineChart') {
      return <LineChart {...this.props.chart} />
    // } else if (type === 'ChoroplethMap') {
    //   return <ChoroplethMap {...this.props.chart} />
    } else if (type === 'MapChart') {
      return <MapChart {...this.props.chart} onMapClick={this.props.primaryChartClick}/>
    } else if (type === 'ColumnChart') {
      return <ColumnChart {...this.props.chart} {...this.props.chart} updateTypeParams={this.props.updateTypeParams}/>
    } else if (type === 'BubbleMap') {
      return <BubbleMapChart {...this.props.chart} />
    } else if (type === 'BarChart') {
      return <BarChart {...this.props.chart} />
    } else {
      return <DatapointTable {...this.props.chart} />
    }
  },

  render: function () {
    const chart = this.props.chart

    const chart_selector = (
      <div>
        <br/><h4>or</h4><br/>
        <ChartSelect charts={this.state.all_charts.raw} selectChart={this.props.selectChart} />
      </div>
    )

    const chart_type_selector = (
      <div className='medium-10 medium-centered text-center columns' style={{position: 'relative', marginTop: '-1.5rem', padding: '4rem 0'}}>
        <h4>View Data As TEST GULP 222 </h4>
        <ChartTypeSelect onChange={this.props.setType} selected={this.props.chart.type}/>
        { this.props.selectChart ? chart_selector : null }
      </div>
    )

    const missing_indicators = _.isEmpty(chart.selected_indicators)
    const missing_locations = _.isEmpty(chart.selected_locations)
    let chart_placeholder = <Placeholder height={300}/>
    if (!chart.loading && (missing_indicators || missing_locations)) {
      let placeholder_text = 'Select a(n) '
      placeholder_text += missing_indicators ? 'INDICATOR ' : ''
      placeholder_text += missing_locations && missing_indicators ? 'and ' : ''
      placeholder_text += missing_locations ? 'LOCATION ' : ''
      chart_placeholder = <Placeholder height={300} text={placeholder_text} loading={false}/>
    } else if (_.isEmpty(chart.data) && !_.isNull(chart.data) && chart.loading) {
      chart_placeholder = <Placeholder height={300} text='NO DATA' loading={false}/>
    }

    const sidebar = (
      <aside className='medium-4 large-4 medium-push-8 large-push-8 columns animated slideInRight'>
        <MultiChartControls {...this.props} className='row collapse' />
      </aside>
    )

    const chart_classes = !chart.editMode ? 'medium-12 ' : 'medium-8 large-8 medium-pull-4 large-pull-3 '

    return (
      <article className='multi-chart medium-12 columns' style={chart.type === 'RawData' ? {overflowX: 'auto'} : null}>
        <MultiChartHeader {...this.props}/>
        <section className='row'>
          { chart.editMode ? sidebar : null }
          <div className={chart_classes + ' columns chart-zone'}>
            {
              chart.selectTypeMode ? chart_type_selector : (
                !_.isEmpty(chart.data) ? this.getChartComponentByType(chart.type) : chart_placeholder
              )
            }
          </div>
        </section>
      </article>
    )
  }
})

export default MultiChart
