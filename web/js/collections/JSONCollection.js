var app = app || {};

(function() {
    'use strict';

    app.JSONCollection = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: app.JSONModel,
        url: 'http://127.0.0.1:9000/insight/api/v1.0/models'
    });
})();