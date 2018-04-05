var app = app || {};

(function() {
    'use strict';

    app.DatasetCollection = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: app.DatasetModel,
        url: '/insight/api/v1.0/datasets',
        comparator: function(item) {
            return item.get('name');
        }
    });
})();
