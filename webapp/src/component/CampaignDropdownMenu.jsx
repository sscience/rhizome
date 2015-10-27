'use strict';

var _      = require('lodash');
var React  = require('react');
var moment = require('moment');

var DropdownMenu     = require('component/DropdownMenu.jsx');
var CampaignMenuItem = require('component/CampaignMenuItem.jsx');

function searchValue(campaign) {
  var m = moment(campaign.start_date);

  // Include several possible date formats for matching against
  return [
    m.format('YYYY-MM'),
    m.format('MM-YYYY'),
    m.format('YYYY-M'),
    m.format('M-YYYY'),
    m.format('MMMM YYYY'),
    m.format('YYYY/MM'),
    m.format('MM/YYYY'),
    m.format('YYYY/M'),
    m.format('M/YYYY'),

    m.format('YY-MM'),
    m.format('MM-YY'),
    m.format('YY-M'),
    m.format('M-YY'),
    m.format('MMMM YY'),
    m.format('YY/MM'),
    m.format('MM/YY'),
    m.format('YY/M'),
    m.format('M/YY'),
  ].join(' ');
}

var CampaignDropdownMenu = React.createClass({
  propTypes : {
    campaigns : React.PropTypes.array.isRequired,
    sendValue : React.PropTypes.func.isRequired
  },

  getInitialState : function () {
    return {
      pattern : ''
    };
  },

  render : function () {
    var self = this;

    var re = new RegExp(this.state.pattern);

    // If the pattern is longer than two characters, filter the list with it,
    // otherwise, return true to include all campaigns in the dropdown
    var filterCampaigns = !_.isEmpty(this.state.pattern)?
      _.flow(searchValue, function (v) { return re.test(v); }) :
      _.constant(true);

    var campaigns = _(this.props.campaigns)
      .filter(filterCampaigns)
      .sortBy(_.method('start_date.getTime'))
      .reverse()
      .map(function (campaign) {
        let slug = campaign.office.name + ' ' + moment(campaign.start_date).format('MMMM YYYY')
        return (
          <CampaignMenuItem key={'campaign-' + campaign.id}
            sendValue={self.props.sendValue}
            id={campaign.id}
            slug={slug}
            management_dash_pct_complete={campaign.management_dash_pct_complete}
            />
        );
      })
      .value();

    var props = _.omit(this.props, 'campaigns', 'sendValue');

    return (
      <DropdownMenu icon='fa-calendar'
        searchable={true}
        onSearch={this._setPattern}
        {...props}>

        {campaigns}

      </DropdownMenu>
    );
  },

  _setPattern : function (value) {
    this.setState({ pattern : value })
  }
});

module.exports = CampaignDropdownMenu;
