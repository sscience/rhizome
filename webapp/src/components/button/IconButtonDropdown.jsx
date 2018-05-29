import React from 'react'
import IconButton from 'components/button/IconButton'
import Dropdown from 'components/dropdown/Dropdown'

class IconButtonDropdown extends Dropdown {

  static propTypes = {
    className: React.PropTypes.string,
    color: React.PropTypes.string,
    text: React.PropTypes.string.isRequired,
    icon: React.PropTypes.string,
    searchable: React.PropTypes.bool,
    onSearch: React.PropTypes.func
  }

  static defaultProps = {
    icon: 'fa-bars',
    onSearch: () => null
  }

  componentWillReceiveProps = function (nextProps) {
    if (nextProps.text !== this.props.text) {
      this.setState({ open: false })
    }
  }

  render = function () {
    return (
      <IconButton {...this.props} onClick={this._toggleMenu}/>
    )
  }
}

export default IconButtonDropdown
