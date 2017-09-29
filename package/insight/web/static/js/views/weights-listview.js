var app = app || {};

(function($) {
    'use strict';
    app.WeightsListView = Backbone.View.extend({
        el: '#weights-table-body',

        initialize: function() {
            this.collection = new app.WeightsCollection();
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
                this.$el.append(new app.WeightsView({
                    model: model
                }).el);
            }, this);
            return this;
        }
    });
})(jQuery);