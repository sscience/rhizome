import React from 'react'

import HighChart from 'components/molecules/highcharts/HighChart'
import palettes from 'utilities/palettes'
import format from 'utilities/format'

class MapChart extends HighChart {

  setConfig = function () {
    const current_indicator = this.props.selected_indicators[0]
    const palette = palettes[this.props.palette]
    const integerWithBounds = current_indicator.data_format === 'int' && current_indicator.good_bound < 2 && current_indicator.bad_bound < 2
    this.config = {
      series: this.setSeries(),
      colorAxis: {min: 0},
      mapNavigation: {
        enabled: true,
        enableMouseWheelZoom: false,
        buttonOptions: {
          verticalAlign: 'bottom'
        }
      }
    }

    if (!integerWithBounds) {
      this.config.colorAxis = {
        dataClasses: this.getDataClasses(current_indicator, palette),
        reversed: current_indicator.good_bound < current_indicator.bad_bound
      }
      this.config.legend = {
        layout: 'vertical',
        align: 'right',
        itemStyle: {
          'fontSize': '14px'
        },
        labelFormatter: function () {
          const boundTo = !isNaN(this.to) ? format.autoFormat(this.to, current_indicator.data_format) : null
          const boundFrom = !isNaN(this.from) ? format.autoFormat(this.from, current_indicator.data_format) : null
          const isBool = current_indicator.data_format === 'bool'
          return (
                (boundFrom || (isBool ? '' : '0')) +
                (isBool ? '': boundTo ? ' - ' : ' ') +
                (boundTo || (isBool ? '' : '+'))
          )
        }
      }
    }

    const clickMap = this.props.onMapClick
    if (clickMap) {
      this.config.plotOptions = {
        series: {
          cursor: 'pointer',
          point: {
            events: {
              click: function (e) {
                clickMap(this.location_id)
              }
            }
          }
        }
      }
    }
  }

  setSeries = function () {
    const props = this.props
    const current_indicator = this.props.selected_indicators[0]
    return [{
      data: this.props.datapoints.meta.chart_data,
      mapData: {'features': this.props.features, 'type': 'FeatureCollection'},
      joinBy: 'location_id',
      name: current_indicator.name,
      borderColor: 'black',
      nullColor: '#D3D3D3',
      states: {
        hover: {
          color: "rgba(163, 232, 255, 1.0)"
        }
      },
      tooltip: {
        pointFormatter: function() {
          return (
            `<span> ${props.locations_index[this.location_id].name}:
            <strong> ${format.autoFormat(this.value, current_indicator.data_format)} </strong>
            </span>`
          )
        }
      }
    }]
  }

  getDataClasses = function (current_indicator, palette) {
    if (current_indicator.good_bound < current_indicator.bad_bound) {
      let temp_bound = current_indicator.good_bound
      current_indicator.good_bound = current_indicator.bad_bound
      current_indicator.bad_bound = temp_bound
      palette = palette.reverse()
    }
    let dataClasses = null
    if (current_indicator.data_format === 'bool') {
      dataClasses = [{to: current_indicator.bad_bound,color: palette[0]},
                     {from: current_indicator.good_bound,color: palette[2]}]
    } else {
      dataClasses = [{from:0, to:current_indicator.bad_bound, color:palette[0]},
                     {from:current_indicator.bad_bound, to:current_indicator.good_bound, color:palette[1]},
                     {from:current_indicator.good_bound, color:palette[2]}]
    }
    return dataClasses
  }
}

export default MapChart
