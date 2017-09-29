var app = app || {};

(function() {
    'use strict';

    app.DatasetModel = Backbone.Model.extend({
        urlRoot: '/insight/api/v1.0/datasets',
        idAttribute: 'name',
        defaults: {
            name: '',
            size: ''
        },
    });
})();