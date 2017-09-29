var app = app || {};

(function() {
    'use strict';

    app.WeightsCollection = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: app.WeightsModel,
        url: '/insight/api/v1.0/weights'
    });
})();