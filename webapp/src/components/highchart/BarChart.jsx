import _ from 'lodash'
import React from 'react'

import HighChart from 'components/highchart/HighChart'
import format from 'utilities/format'

class BarChart extends HighChart {

  setConfig () {
    const first_indicator = this.props.selected_indicators[0]
    this.config = {
      chart: { type: 'bar' },
      xAxis: {
        type: 'datetime',
        labels: {
          format: '{value:%b %d, %Y}'
        }
      },
      yAxis: {
        title: { text: '' },
        labels: {
          formatter: function () {
            return format.autoFormat(this.value, first_indicator.data_format)
          }
        }
      },
      tooltip: {
        pointFormatter: function (point) {
          const value = format.autoFormat(this.y, first_indicator.data_format, 1)
          return `${this.series.name}: <b>${value}</b><br/>`
        }
      },
      series: this.setSeries()
    }
  }

  setSeries () { console.info('------ BarChart.setSeries')
    const data = this.props.datapoints.melted
    const groupByIndicator = this.props.groupBy === 'indicator'
    const grouped_data = groupByIndicator ? _.groupBy(data, 'indicator.id') : _.groupBy(data, 'location.id')
    const series = []
    _.forEach(grouped_data, group => {
      _.sortBy(group, _.method('campaign.start_date.getTime'))
      series.push({
        name: groupByIndicator ? group[0].indicator.name : group[0].location.name,
        data: group.map(datapoint => datapoint.value) // Needs to be sorted by date
      })
    })
    return series
  }
}

export default BarChart
