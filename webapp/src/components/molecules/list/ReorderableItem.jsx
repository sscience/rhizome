import React from 'react'
import IconButton from 'components/atoms/IconButton'

export default React.createClass({
  propTypes: {
    item: React.PropTypes.object.isRequired
  },
  render: function () {
    let item = this.props.item
    return (
      <div key={item.id}>{item.name}
        <IconButton className='clear-btn' onClick={() => item.removeFunction(item.id)} icon='fa-times-circle' />
      </div>
    )
  }
})

