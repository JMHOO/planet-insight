var app = app || {};

(function() {
    'use strict';


    app.JSONModel = Backbone.Model.extend({
        // Default attributes for the todo
        // and ensure that each todo created has `title` and `completed` keys.
        defaults: {
            model_name: '',
            model_defination: ''
        },

        save: function() {

        }
    });
})();