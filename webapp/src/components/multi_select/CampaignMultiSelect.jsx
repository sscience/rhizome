import _ from 'lodash'
import React, {Component, PropTypes} from 'react'
import Reflux from 'reflux'
import ReorderableList from 'components/list/ReorderableList'
import DropdownButton from 'components/button/DropdownButton'
import CampaignSelect from 'components/select/CampaignSelect'
import SwitchButton from 'components/form/SwitchButton'

import CampaignStore from 'stores/CampaignStore'

class CampaignMultiSelect extends Component {

  static propTypes = {
    campaigns: PropTypes.shape({
      raw: PropTypes.array,
      list: PropTypes.array
    }).isRequired,
    selected_campaigns: PropTypes.array,
    setCampaigns: PropTypes.func,
    linkCampaigns: PropTypes.func,
    selectCampaign: PropTypes.func,
    deselectCampaign: PropTypes.func,
    clearSelectedCampaigns: PropTypes.func,
    classes: PropTypes.string,
    linked: PropTypes.bool,
    multi: PropTypes.bool
  }

  static defaultProps = {
    multi: false,
    linked: false,
    selected_campaigns: []
  }

  render () {
    const props = this.props
    const raw_campaigns = props.campaigns.raw || []
    let selected_campaigns = !_.isEmpty(props.selected_campaigns) ? props.selected_campaigns : raw_campaigns
    if (props.multi) {
      return (
        <form className={props.classes}>
          <h3>Campaigns
            <DropdownButton
              items={raw_campaigns}
              sendValue={this.props.selectCampaign}
              item_plural_name='Campaigns'
              style='icon-button right'
              icon='fa-plus'
            />
          </h3>
          <a className='remove-filters-link' onClick={this.props.clearSelectedCampaigns}>Remove All </a>
          <List items={selected_campaigns} removeItem={this.props.deselectCampaign} />
        </form>
      )
    } else {
      const filtered_by_campaign = props.selected_campaigns.length > 0
      const toggleFilterByCampaign = () => filtered_by_campaign ? this.props.setCampaigns([]) : this.props.setCampaigns(raw_campaigns[0])
      return (
        <div className={props.classes}>
          <h3>
            Campaign Filter <a onClick={this.props.linkCampaigns}><i className={'fa ' + (this.props.linked ? 'fa-chain ' : 'fa-chain-broken') }/></a>
            <SwitchButton
              name='filterByCampaign'
              title='filterByCampaign'
              id='filterByCampaign'
              checked={filtered_by_campaign}
              onChange={toggleFilterByCampaign}
            />
          </h3>
          {
            filtered_by_campaign ? (
              <CampaignSelect
                campaigns={raw_campaigns}
                selected={selected_campaigns[0]}
                sendValue={this.props.setCampaigns}/>
            ) : null
          }
          <br/>
        </div>
      )
    }
  }
}



export default CampaignMultiSelect
