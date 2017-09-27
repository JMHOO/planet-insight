var app = app || {};

(function() {
    'use strict';

    app.JSONCollection = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: app.JSONModel,
        url: '/insight/api/v1.0/models'
    });
})();