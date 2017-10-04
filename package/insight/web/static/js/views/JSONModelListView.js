var app = app || {};

(function($) {
    'use strict';

    // Todo Item View
    // --------------  
    app.JSONModelsListView = Backbone.View.extend({
        el: '#list_json_models',


        initialize: function() {
            this.collection = new app.JSONCollection();

            this.collection.fetch({ reset: true });
            this.render();

            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
            //this.model.on('change', this.render, this);
        },

        reload: function() {
            this.collection.reset();
            this.collection.fetch({ reset: true });
            this.render();
        },

        render: function() {
            this.$el.html('');
            var count = 0;
            var row;
            this.collection.each(function(item) {
                if (count % 2 == 0) {
                    row = $('<div/>').addClass("row");
                    this.$el.append(row)
                    row.append(this.renderModel(item));
                } else {
                    row.append(this.renderModel(item));
                }
                count++;
            }, this);

            $('pre code').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        renderModel: function(item) {
            var modelView = new app.JSONModelView({
                model: item
            });
            return modelView.render().el;
        },

    });
})(jQuery);