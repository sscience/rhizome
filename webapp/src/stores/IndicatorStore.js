'use strict';

var _      = require('lodash');
var Reflux = require('reflux');

var api = require('data/api');

var IndicatorStore = Reflux.createStore({

	listenables : [require('actions/AppActions')],

	init : function () {
		this.indicators = [];
	},

	getInitialState : function () {
		return {
			indicators : this.indicators
		};
	},

	onInit : function () {
		api.indicators().then(function (response) {
			var indicators = response.objects;
			this.indicators = _.indexBy(indicators, 'id');
			this.trigger({ indicators : indicators });

		}.bind(this));
	},

	getById : function () {
		console.log('==get indicator by id ===')
		console.log('==get indicator by id ===')
		return _(arguments)
			.map(function (id) {
				// console.log(id)
				// console.log('==id==')
				return this.indicators[id];
			}.bind(this))
			.filter()
			.value();
	},

});

module.exports = IndicatorStore;
