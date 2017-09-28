var app = app || {};

(function() {
    'use strict';

    app.Task = Backbone.Model.extend({

        urlRoot: '/insight/api/v1.0/jobs',
        idAttribute: 'instance_name',

        defaults: {
            instance_name: '',
            model_name: '',
            dataset_name: '',
            epochs: '',
            job_status: '',
            created: ''
        },

        save: function() {

        }
    });
})();