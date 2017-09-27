var app = app || {};

(function() {
    'use strict';


    app.Task = Backbone.Model.extend({
        // Default attributes for the todo
        // and ensure that each todo created has `title` and `completed` keys.
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