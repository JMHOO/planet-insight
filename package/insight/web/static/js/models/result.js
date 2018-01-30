var app = app || {};

(function() {
    'use strict';

    app.Result = Backbone.Model.extend({
        urlRoot: '/insight/api/v1.0/results',
        idAttribute: 'instance_name',

        defaults: {
            instance_name: '',
            model_name: '',
            dataset_name: '',
            epochs: '',
            job_status: '',
            created: '',
            status_color: ''
        },

        save: function() {

        }
    });
})();
