var app = app || {};

(function() {
    'use strict';

    app.TaskLogs = Backbone.Collection.extend({
        initialize: function(instance_name) {
            this.instance_name = instance_name;
        },

        url: function() {
            return '/insight/api/v1.0/jobs/' + this.instance_name + '/logs';
        },

        model: app.TaskLog
    });
})();