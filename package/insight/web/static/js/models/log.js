var app = app || {};

(function() {
    'use strict';

    app.TaskLog = Backbone.Model.extend({
        defaults: {
            info: '',
            train: ''
        },

        save: function() {

        }
    });
})();