import React from 'react'
import IconButton from 'components/atoms/IconButton'

var DropdownIcon = React.createClass({

  mixins: [
    require('components/molecules/menus/MenuControl')
  ],

  propTypes: {
    className: React.PropTypes.string,
    text: React.PropTypes.string.isRequired,
    icon: React.PropTypes.string,
    searchable: React.PropTypes.bool,
    onSearch: React.PropTypes.func
  },

  getDefaultProps: function () {
    return {
      icon: 'fa-bars'
    }
  },

  componentWillReceiveProps: function (nextProps) {
    if (nextProps.text !== this.props.text) {
      this.setState({ open: false })
    }
  },

  render: function () {
    return (
      <IconButton {...this.props} />
    )
  }
})

export default DropdownIcon