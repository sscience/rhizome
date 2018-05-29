import _ from 'lodash'
import React, {Component, PropTypes} from 'react'

import Select from 'components/select/Select'
import ExpandableMenuItem from 'components/dropdown/ExpandableMenuItem'

class LocationSelect extends Component {

  constructor (props) {
    super(props)
    this.state = {
      pattern: ''
    }
  }

  static propTypes = {
    locations: PropTypes.array.isRequired,
    selected: PropTypes.object.isRequired,
    sendValue: PropTypes.func.isRequired,
    hideLastLevel: PropTypes.bool
  }

  static defaultProps = {
    locations: [],
    selected: {'name': 'Loading ...'}
  }

  shouldComponentUpdate (nextProps, nextState) {
    return nextProps.locations.length !== this.props.locations.length ||
      nextProps.selected.id !== this.props.selected.id
  }

  _setPattern = (value) => {
    this.setState({ pattern: value })
    this.forceUpdate()
  }

  _buildLocations (original_locations, pattern) {
    var locations = original_locations.map(r => {
      return {
        title: r.name,
        value: r.id,
        parent: r.parent_location_id
      }
    })

    if (pattern.length > 2) {
      locations = locations.filter(r => new RegExp(pattern, 'i').test(r.title))
    } else {
      var idx = _.indexBy(locations, 'value')
      locations = []
      _.each(idx, location => {
        if (idx.hasOwnProperty(location.parent)) {
          var p = idx[location.parent]
          var children = p.children || []

          children.push(location)
          p.children = _.sortBy(children, 'title')
        } else {
          locations.push(location)
        }
      })
    }

    return locations
  }

  render = () => {
    const props = this.props
    const locations = this._buildLocations(props.locations, this.state.pattern)
    const sorted_locations = _.sortBy(locations, 'title')
    const selected_text = !props.selected.id && locations.length > 0 ? 'Select Location' : props.selected.name
    const menu_items = sorted_locations.map(location => {
      return <ExpandableMenuItem key={location.value} sendValue={props.sendValue} {...location} hideLastLevel={props.hideLastLevel}/>
    })

    return (
      <Select
        className='font-weight-600 cd-titlebar-margin'
        icon='fa-chevron-down'
        text={selected_text}
        searchable
        onSearch={this._setPattern}>
        {menu_items}
      </Select>
    )
  }
}

export default LocationSelect
