var app = app || {};

(function() {
    'use strict';

    app.WeightsModel = Backbone.Model.extend({
        urlRoot: '/insight/api/v1.0/weights',
        idAttribute: 'name',
        defaults: {
            name: '',
            size: ''
        },
    });
})();