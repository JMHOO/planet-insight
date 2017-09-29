var app = app || {};

(function($) {
    'use strict';
    app.DatasetListView = Backbone.View.extend({
        el: '#dataset-table-body',

        initialize: function() {
            this.collection = new app.DatasetCollection();
            this.collection.fetch({ reset: true });

            this.render();
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
        },

        refresh: function() {
            this.collection.fetch({ reset: true });
        },

        render: function() {
            this.$el.html('');
            this.collection.each(function(model) {
                this.$el.append(new app.DatasetView({
                    model: model
                }).el);
            }, this);
            return this;
        }
    });
})(jQuery);