var app = app || {};

(function($) {
    'use strict';
    app.WorkerListView = Backbone.View.extend({
        el: '#cluster-table-body',

        initialize: function() {
            this.collection = new app.WorkerCollection();
            this.collection.fetch({ reset: true });

            this.render();
            this.listenTo(this.collection, 'reset', this.render);
        },

        refresh: function() {
            this.collection.fetch({ reset: true });
        },

        render: function() {
            this.$el.html('');
            this.collection.each(function(model) {
                this.$el.append(new app.WorkerView({
                    model: model
                }).el);
            }, this);
            return this;
        }
    });
})(jQuery);