var app = app || {};

(function() {
    'use strict';

    app.TaskCollection = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: app.Task,
        url: '/insight/api/v1.0/jobs',
        comparator: function(item) {
            return item.get('Name');
            }
    });

//    app.TaskCollection.sort();

})();
