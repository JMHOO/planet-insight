var app = app || {};

(function() {
    'use strict';

    app.WorkerCollection = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: app.Worker,
        url: '/insight/api/v1.0/workers'
    });
})();