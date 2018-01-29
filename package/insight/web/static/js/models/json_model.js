var app = app || {};

(function() {
    'use strict';

    app.JSONModel = Backbone.Model.extend({
        urlRoot: '/insight/api/v1.0/models',
        idAttribute: 'model_name',
        defaults: {
            model_name: '',
            model_defination: ''
        },
    });
})();
