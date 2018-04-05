var app = app || {};

(function($) {
    'use strict';
    app.ResultListView = Backbone.View.extend({
        el: '#results-table-body',

        initialize: function() {
            this.collection = new app.ResultCollection();
            this.collection.fetch({ reset: true });

            this.render();
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
        },

        refresh: function() {
            this.collection.fetch({ reset: true });
        },

        // render library by rendering each book in its collection
        render: function() {
            this.$el.html('');
            this.collection.each(function(model) {
                this.$el.append(new app.ResultView({
                    model: model
                }).el);
            }, this);
            return this;
        }
    });
})(jQuery);
