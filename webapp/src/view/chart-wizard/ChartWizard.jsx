import React from 'react'

import ChartWizardStep from './ChartWizardStep.jsx'
import ChartWizardStepList from './ChartWizardStepList.jsx'
import ChartWizardScreen from './ChartWizardScreen.jsx'
import ChartWizardScreenList from './ChartWizardScreenList.jsx'

const chartDef = {"title":"Polio Case","type":"LineChart","indicators":[168],"locations":"selected","groupBy":"indicator","x":0,"y":0,"xFormat":",.0f","yFormat":",.0f","timeRange":null,"id":22}

let ChartWizard = React.createClass({
  getInitialState() {
    return {
      refer: 'country'
    }
  },

  createChart() {
    this.props.save(chartDef)
  },

  activeStep(refer) {
    this.setState({
      refer: refer
    })
  },

  render() {
    let previewStep = (
      <div>
        <input type='text' value={chartDef.title} />
        <a href="#" className="button success" onClick={this.createChart}>
          {this.props.chartDef ? "Update Chart" : "Create Chart"}
        </a>
      </div>
    )

    return (
      <div className='chart-wizard'>
        <ChartWizardStepList onToggle={this.activeStep} active={this.state.refer}>
          <ChartWizardStep title='Select Country' refer='country'>
            <p>select country here</p>
          </ChartWizardStep>
          <ChartWizardStep title='Select Indicator' refer='indicator'>
            <p>select indicators here</p>
          </ChartWizardStep>
          <ChartWizardStep title='Select Location' refer='location'>
            <p>select location here</p>
          </ChartWizardStep>
          <ChartWizardStep title='Select Campaign' refer='campaign'>
            <p>select campaign here</p>
          </ChartWizardStep>
          <ChartWizardStep title='Select Chart Type' refer='chart-type'>
            <p>select chart type here</p>
          </ChartWizardStep>
          <ChartWizardStep title='Customise Styles' refer='style'>
            <p>Customise styles here</p>
          </ChartWizardStep>
          <ChartWizardStep title='Preview' refer='preview'>
            {previewStep}
          </ChartWizardStep>
        </ChartWizardStepList>
        <ChartWizardScreenList active={this.state.refer}>
          <ChartWizardScreen referTo='country'>
            <h1>Select country page</h1>
          </ChartWizardScreen>
          <ChartWizardScreen referTo='indicator'>
            <h1>Select indicator page</h1>
          </ChartWizardScreen>
          <ChartWizardScreen referTo='location'>
            <h1>Select location page</h1>
          </ChartWizardScreen>
          <ChartWizardScreen referTo='campaign'>
            <h1>Select campaign page</h1>
          </ChartWizardScreen>
          <ChartWizardScreen referTo='chart-type'>
            <h1>Select Chart type page</h1>
          </ChartWizardScreen>
          <ChartWizardScreen referTo='style'>
            <h1>Customise style page</h1>
          </ChartWizardScreen>
          <ChartWizardScreen referTo='preview'>
            <h1>Preview page</h1>
          </ChartWizardScreen>
        </ChartWizardScreenList>
        <a className='chart-wizard__cancel' href="#" onClick={this.props.cancel}>Cancel without saving chart</a>
      </div>
    )
  }
})

export default ChartWizard
