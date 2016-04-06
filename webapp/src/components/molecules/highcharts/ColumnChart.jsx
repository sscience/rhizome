import _ from 'lodash'
import d3 from 'd3'
import React, { PropTypes } from 'react'

import HighChart from 'components/molecules/highcharts/HighChart'
import format from 'components/molecules/charts/utils/format'
import palettes from 'components/molecules/charts/utils/palettes'
import aspects from 'components/molecules/charts/utils/aspects'

class ColumnChart extends HighChart {

  setData () { console.info('------ ColumnChart.setData')
    const props = this.props
    const selected_locations_index = _.indexBy(props.selected_locations, 'id')
    const selected_indicators_index = _.indexBy(props.selected_indicators, 'id')

  }

  setOptions () { console.info('------ ColumnChart.setOptions')
    const options = this.options
    const props = this.props
  }
}

export default ColumnChart

