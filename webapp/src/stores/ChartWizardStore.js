import Reflux from 'reflux'
import _ from 'lodash'
import moment from 'moment'

import ChartWizardActions from 'actions/ChartWizardActions'

import api from 'data/api'
import ChartDataInit from 'data/chartDataInit'
import builderDefinitions from 'stores/chartBuilder/builderDefinitions'
import treeify from 'data/transform/treeify'
import ancestryString from 'data/transform/ancestryString'

let ChartWizardStore = Reflux.createStore({
  listenables: ChartWizardActions,
  data: {
    indicatorList: [],
    indicatorSelected: [],
    indicatorFilteredList: [],
    countries: [],
    countrySelected: [],
    location: [],
    location_tags: [ // Temporarily Hard Coded. Fetch from API in the future
      {
        value: 1,
        title: 'LPD 1',
        location_ids: [ 3148, 3149, 3143, 3300, 3303, 3304, 3311, 3298, 3214, 3206, 3213, 3200, 3201, 3204, 3400, 3389, 3395, 3401, 3493 ]
      },
      {
        value: 2,
        title: 'LPD 2',
        location_ids: [ 3142, 3279, 3309, 3302, 3305, 3327, 3184, 3515, 3209, 3211, 3212, 3199, 3207, 3210, 3311, 3203, 3367, 3360, 3363, 3369, 3398, 3404, 3388, 3405, 3409, 3427, 3494, 3508 ]
      },
      {
        value: 3,
        title: 'LPD 3',
        location_ids: [ 3248, 3249, 3256, 3251, 3273, 3283, 3117, 3291, 3295, 3301, 3308, 3306, 3307, 3343, 3344, 3351, 3355, 3356, 3370, 3371, 3373, 3372, 3361, 3364, 3365, 3187, 3190, 3189, 3191, 3376, 3397, 3391, 3393, 3408, 3419, 3420, 3446, 3447, 3463, 3495, 3492, 3515, 3506, 3507, 3509, 3510, 3505, 3512, 3513]
      }
    ],
    locationList: [],
    locationFilteredList: [],
    selected_locations: [],
    campaignFilteredList: [],
    // timeRangeFilteredList: [],
    chartTypeFilteredList: [],
    groupByValue: 0,
    locationLevelValue: 0,
    timeValue: 0,
    yFormatValue: 0,
    xFormatValue: 0,
    canDisplayChart: false,
    isLoading: true,
    chartOptions: {},
    chartData: [],
    chartDef: {},
    rawIndicators: null,
    rawTags: null,
    xLabel: null,
    yLabel: null,
    startDate: null,
    endDate: null
  },
  LAYOUT_PREVIEW: 0,

  filterIndicatorByCountry (indicators, countries) {
    let countryId = countries.map(c => c.id)
    if (countryId.length) {
      return indicators.filter(indicator => {
        let officeId = indicator.office_id.filter(id => !!id)
        return countryId.map(id => {
          return officeId.indexOf(id) >= 0
        }).reduce((a, b) => a && b, true)
      })
    } else {
      return []
    }
  },

  filterLocationByCountry (locations, countries) {
    let countryId = countries.map(c => c.id)
    return locations.filter(location => {
      return countryId.indexOf(location.value) >= 0 || countryId.indexOf(location.office_id) >= 0
    })
  },

  filterCampaignByCountry (campaigns, countries) {
    let countryId = countries.map(c => c.id)
    return campaigns.filter(campaign => {
      return countryId.indexOf(campaign.office_id) >= 0
    })
  },

  // filterTimeRangeByChartType (timeRanges, chartType) {
  //   let expectTimes = _.find(builderDefinitions.charts, { name: chartType }).timeRadios
  //   return timeRanges.filter(time => {
  //     return _.includes(expectTimes, time.value)
  //   })
  // },

  // filterChartTypeByIndicator () {
  //   api.chartType({ primary_indicator_id: this.data.indicatorSelected[0].id }, null, {'cache-control': 'no-cache'}).then(res => {
  //     let availableCharts = res.objects.map(chart => {
  //       return chart.name
  //     })
  //     this.data.chartTypeFilteredList = builderDefinitions.charts.filter(chart => {
  //       return _.includes(availableCharts, chart.name)
  //     })
  //
  //     if (!_.includes(availableCharts, this.data.chartDef.type)) {
  //       this.onChangeChart(this.data.chartTypeFilteredList[0].name)
  //     }
  //   })
  // },

  applyChartDef (chartDef) {
    this.data.locationLevelValue = Math.max(_.findIndex(builderDefinitions.locationLevels, { value: chartDef.locations }), 0)
    this.data.groupByValue = Math.max(_.findIndex(builderDefinitions.groups, { value: chartDef.groupBy }), 0)
    this.data.timeValue = Math.max(_.findIndex(this.data.timeRangeFilteredList, { json: chartDef.timeRange }), 0)
    this.data.yFormatValue = Math.max(_.findIndex(builderDefinitions.formats, { value: chartDef.yFormat }), 0)
    this.data.xFormatValue = Math.max(_.findIndex(builderDefinitions.formats, { value: chartDef.xFormat }), 0)

    this.data.chartDef.locations = builderDefinitions.locationLevels[this.data.locationLevelValue].value
    this.data.chartDef.groupBy = builderDefinitions.groups[this.data.groupByValue].value
    // this.data.chartDef.timeRange = this.data.timeRangeFilteredList[this.data.timeValue].json
    this.data.chartDef.yFormat = builderDefinitions.formats[this.data.yFormatValue].value
    this.data.chartDef.xFormat = builderDefinitions.formats[this.data.xFormatValue].value
  },

  getInitialState () {
    return this.data
  },

  async onInitialize (chartDef) {
    this.data.chartDef = _.clone(chartDef)

    let locations = await api.locations()
    let campaigns = await api.campaign()
    let offices = await api.office()

    this.locationIndex = _.indexBy(locations.objects, 'id')
    this.data.country = offices.objects[0]

    this.data.countries.forEach((country, index) => {
      country.value = country.title = country.name
      country.index = index
    })
    let countryIndex = _.indexBy(this.data.countries, _.property('id'))
    this.data.countrySelected = (this.data.chartDef.countries || []).map(country => {
      return countryIndex[country]
    })
    this.data.locationList = _(locations.objects)
      .map(location => {
        return {
          'title': location.name,
          'value': location.id,
          'parent': location.parent_location_id
        }
      })
      .sortBy('title')
      .reverse()
      .thru(_.curryRight(treeify)('value'))
      .map(ancestryString)
      .value()

    // hacky way to set the default location //
    if (!this.data.chartDef.locationValue){
      this.data.chartDef.locationValue = locations.objects[0].id
    }

    this.data.selected_locations = this.data.chartDef.locationValue
      ? Array.isArray(this.data.chartDef.locationValue)
        ? this.data.chartDef.locationValue.map(location => this.locationIndex[location])
        : [this.locationIndex[this.data.chartDef.locationValue]]
      : []

    this.data.rawIndicators = await api.indicators(null, null, { 'cache-control': 'no-cache' })
    this.data.rawTags = await api.get_indicator_tag(null, null, { 'cache-control': 'no-cache' })
    this.indicators = this.data.rawIndicators.objects

    this.data.indicatorFilteredList = this.indicators // this.filterIndicatorByCountry(this.indicators, this.data.countrySelected)
    let indicatorTree = api.buildIndicatorsTree(this.data.indicatorFilteredList, this.data.rawTags.objects, true, true)
    this.indicatorIndex = _.indexBy(this.indicators, 'id')

    // hacky way to find the default indicator //
    if (chartDef.indicators.length === 0){
        chartDef.indicators.push(this.indicators[0].id)
    }

    this.data.indicatorList = _.sortBy(indicatorTree, 'title')
    this.data.indicatorSelected = chartDef.indicators.map(id => {
      return this.indicatorIndex[id]
    })

    let officeIndex = _.indexBy(offices.objects, 'id')
    this.campaignList = _(campaigns.objects)
      .map(campaign => {
        return _.assign({}, campaign, {
          'start_date': moment(campaign.start_date, 'YYYY-MM-DD').toDate(),
          'end_date': moment(campaign.end_date, 'YYYY-MM-DD').toDate(),
          'office': officeIndex[campaign.office_id]
        })
      })
      .sortBy(_.method('start_date.getTime'))
      .reverse()
      .value()

    this.campaignIndex = _.indexBy(this.campaignList, 'id')
    this.data.locationFilteredList = this.data.locationList
    this.data.campaignFilteredList = this.campaignList
    this.data.chartTypeFilteredList = builderDefinitions.charts

    if (this.data.chartDef.campaignValue && this.campaignIndex[chartDef.campaignValue]) {
      this.data.campaign = this.campaignIndex[chartDef.campaignValue]
    } else {
      this.data.campaign = this.data.campaignFilteredList.length > 0
        ? this.data.campaignFilteredList[0]
        : null
    }

    if (!this.data.chartDef.endDate){
        this.data.chartDef.endDate = moment().format('YYYY-MM-DD')
    }

    if (!this.data.chartDef.startDate){
        this.data.chartDef.startDate = moment().subtract(1, 'y').format('YYYY-MM-DD')
    }

    this.applyChartDef(this.data.chartDef)

    this.previewChart()
  },

  onClear () {
    this.data = {
      indicatorList: [],
      indicatorSelected: [],
      indicatorFilteredList: [],
      countries: [],
      countrySelected: [],
      location: [],
      locationList: [],
      locationFilteredList: [],
      campaignFilteredList: [],
      chartTypeFilteredList: [],
      groupByValue: 0,
      locationLevelValue: 0,
      timeValue: 0,
      yFormatValue: 0,
      xFormatValue: 0,
      canDisplayChart: false,
      isLoading: true,
      chartOptions: {},
      chartData: [],
      chartDef: {},
      rawIndicators: null,
      rawTags: null,
      xLabel: null,
      yLabel: null
    }
  },

  onUpdateDateRangePicker: function (key, value) {
    var fullKey = key + 'Date'
    this.data[fullKey] = value
    this.data.chartDef[fullKey] = value
    this.previewChart()
  },

  onEditTitle: function (value) {
    this.data.chartDef.title = value
  },

  onChangeCountry: function (index) {
    _.includes(this.data.countrySelected, this.data.countries[index])
      ? _.remove(this.data.countrySelected, this.data.countries[index])
      : this.data.countrySelected.push(this.data.countries[index])

    this.data.indicatorFilteredList = this.filterIndicatorByCountry(this.indicators, this.data.countrySelected)
    let indicatorTree = api.buildIndicatorsTree(this.data.indicatorFilteredList, this.data.rawTags.objects, true, true)

    this.data.indicatorList = _.sortBy(indicatorTree, 'title')
    this.data.indicatorSelected = this.filterIndicatorByCountry(this.data.indicatorSelected, this.data.countrySelected)

    this.data.locationFilteredList = this.filterLocationByCountry(this.data.locationList, this.data.countrySelected)
    this.data.selected_locations = this.filterLocationByCountry(this.data.selected_locations, this.data.countrySelected)
    this.data.campaignFilteredList = this.filterCampaignByCountry(this.campaignList, this.data.countrySelected)
    this.previewChart()
  },

  onAddLocationsByTag: function (index) {
    let locations_to_add = this.data.location_tags.find( tag => tag.value === index)
    _.forEach(locations_to_add.location_ids, function (location_id) {
      if (this.data.selected_locations.map(item => item.id).indexOf(location_id) >= 0) return
      this.data.selected_locations.push(this.locationIndex[location_id])
    }, this)
    this.previewChart()
  },

  onAddLocation: function (index) {
    if (this.data.selected_locations.map(item => item.id).indexOf(index) >= 0) return
    this.data.selected_locations.push(this.locationIndex[index])
    this.previewChart()
  },

  onRemoveLocation: function (index) {
    _.remove(this.data.selected_locations, { id: index })
    this.previewChart()
  },

  onAddFirstIndicator: function (index) {
    this.data.indicatorSelected[0] = this.indicatorIndex[index]
    this.previewChart()
  },

  onAddIndicator: function (index) {
    if (this.data.indicatorSelected.map(indicator => indicator.id).indexOf(index) >= 0) return
    this.data.indicatorSelected.push(this.indicatorIndex[index])
    this.data.chartDef.y = index
    this.previewChart()
  },

  onReorderIndicator: function (reorderedIndicators) {
    this.data.indicatorSelected = reorderedIndicators
    this.previewChart()
  },

  onRemoveIndicator: function (id) {
    _.remove(this.data.indicatorSelected, {id: id})
    this.previewChart()
  },

  onAddCampaign: function (index) {
    this.data.campaign = this.campaignIndex[index]
    this.previewChart()
  },

  onChangeChart: function (value) {
    this.data.chartDef.type = value
    // this.data.timeRangeFilteredList = this.filterTimeRangeByChartType(builderDefinitions.times, this.data.chartDef.type)
    // this.data.timeValue = Math.min(this.data.timeValue, this.data.timeRangeFilteredList.length - 1)
    // this.data.chartDef.timeRange = this.data.timeRangeFilteredList[this.data.timeValue].json

    if (value === 'ChoroplethMap') {
      this.data.locationLevelValue = _.findIndex(builderDefinitions.locationLevels, {value: 'sublocations'})
    }
    this.data.chartDef.x = this.data.indicatorSelected[0].id
    this.data.chartDef.y = this.data.indicatorSelected[1] ? this.data.indicatorSelected[1].id : 0
    this.data.chartDef.z = this.data.indicatorSelected[2] ? this.data.indicatorSelected[2].id : 0

    this.data.chartData = []

    this.previewChart()
  },

  onChangeGroupRadio: function (value) {
    this.data.groupByValue = value
    this.data.chartDef.groupBy = builderDefinitions.groups[value].value
    this.previewChart()
  },

  onChangeLocationLevelRadio: function (value) {
    this.data.locationLevelValue = value
    this.previewChart()
  },

  onChangeYFormatRadio: function (value) {
    this.data.yFormatValue = value
    this.data.chartDef.yFormat = builderDefinitions.formats[value].value
    this.previewChart()
  },

  onChangeXFormatRadio: function (value) {
    this.data.xFormatValue = value
    this.data.chartDef.xFormat = builderDefinitions.formats[value].value
    this.previewChart()
  },

  onChangeYAxis: function (value) {
    this.data.indicatorSelected[1] = this.indicatorIndex[value]
    this.data.chartDef.y = value
    this.previewChart()
  },

  onChangeZAxis: function (value) {
    this.data.indicatorSelected[2] = this.indicatorIndex[value]
    this.data.chartDef.z = value
    this.previewChart()
  },

  onChangePalette: function (key) {
    this.data.chartDef.palette = key
    this.previewChart()
  },

  onSetXYAxisLabel: function (xAxisLabel, yAxisLabel) {
    this.data.chartDef.xLabel = xAxisLabel
    this.data.chartDef.yLabel = yAxisLabel
    this.previewChart()
  },

  onSaveChart: function (callback) {
    if (!this.data.chartDef.title){
      window.alert('Please add a Title to your chart')
      return
    }

    callback(
      _.merge(
        this.data.chartDef,
        {
          indicators: this.data.indicatorSelected.map(item => {
            return item.id
          }),
          groupBy: builderDefinitions.groups[this.data.groupByValue].value,
          locations: builderDefinitions.locationLevels[this.data.locationLevelValue].value,
          countries: this.data.countrySelected.map(country => country.id),
          locationValue: this.data.selected_locations.map(location => location.id),
          // campaignValue: this.data.campaign.id,
          // timeRange: this.data.timeRangeFilteredList[this.data.timeValue].json,
          yFormat: builderDefinitions.formats[this.data.yFormatValue].value,
          xFormat: builderDefinitions.formats[this.data.xFormatValue].value
        }, (source, override) => {
          return override
        }
      )
    )
  },

  previewChart () {
    // We use the short_name for ordering becuase that is what defines the xDomain in table.js
    this.data.indicatorOrder = this.data.indicatorSelected.map(indicator => {
      return indicator.short_name
    })

    if (!(this.data.indicatorSelected.length && this.data.campaign && this.data.selected_locations.length)) {
      this.data.canDisplayChart = false
      this.data.isLoading = false
      this.trigger(this.data)
      return
    }

    this.data.isLoading = true
    this.trigger(this.data)

    ChartDataInit.fetchChart(this.data.chartDef, this.data, this.indicatorIndex, this.LAYOUT_PREVIEW).then(chart => {
      this.data.canDisplayChart = true
      this.data.isLoading = false
      this.data.chartOptions = chart.options
      this.data.chartData = chart.data
      this.trigger(this.data)
    })
  }
})

export default ChartWizardStore
