var app = app || {};

(function() {
    'use strict';

    app.Worker = Backbone.Model.extend({
        defaults: {
            worker_name: '',
            current_status: '',
            last_seen: '',
            system_info: '',
            idle: '',
            status_color: ''
        },
    });
})();