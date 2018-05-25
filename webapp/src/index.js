import React from 'react'
import Reflux from 'reflux'
import RefluxPromise from 'reflux-promise'
Reflux.use(RefluxPromise(window.Promise))

React.render(React.createElement(require('components/nav/DashboardNav')), document.getElementById('dashboards-nav'))

const Rhizome = window.Rhizome = {
  Dashboards: function (el) {
    React.render(React.createElement(require('containers/DashboardsContainer')), el)
  },
  Dashboard: function (el, dashboard_id) {
    React.render(React.createElement(require('containers/DashboardContainer'), { dashboard_id: dashboard_id }), el)
  },
  Charts: function (el) {
    React.render(React.createElement(require('containers/ChartsContainer')), el)
  },
  ChartContainer: function (el, chart_id) {
    React.render(React.createElement(require('containers/ChartContainer'), { chart_id: chart_id }), el)
  },
}

if ('ActiveXObject' in window) {
  var body = document.getElementsByTagName('body')[0]
  body.classList.add('ie')
}

export default Rhizome
