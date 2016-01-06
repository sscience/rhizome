import React from 'react'
import Reflux from 'reflux'

import DataBrowserTableStore from 'stores/DataBrowserTableStore'

const {
  Datascope, LocalDatascope
} = require('react-datascope')

let {
  SimpleDataTable, SimpleDataTableColumn,
  Paginator
} = require('react-datascope')

let DatabrowserTable = React.createClass({
  mixins: [Reflux.connect(DataBrowserTableStore)],

  render: function () {
    if (!this.state || !this.state.data) {
      return (<div className='medium-12 columns ds-data-table-empty'>No data.</div>)
    } else {
      let fields = this.state.fields.map(column => (<SimpleDataTableColumn name={column}/>))
      return (<LocalDatascope
          data={this.state.data}
          schema={this.state.schema}
          pageSize={10} >
          <Datascope>
            <SimpleDataTable>
              {fields}
            </SimpleDataTable>
            <Paginator />
          </Datascope>
        </LocalDatascope>)
    }
  }
})

export default DatabrowserTable
