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
            console.log(this.collection);
            this.render();

            this.listenTo(this.collection, 'reset', this.render);
        },

        // render library by rendering each book in its collection
        render: function() {
            this.collection.each(function(item) {
                this.renderModel(item);
            }, this);
        },

        // render a book by creating a BookView and appending the
        // element it renders to the library's element
        renderModel: function(item) {
            var modelView = new app.JSONModelView({
                model: item
            });
            this.$el.append(modelView.render().el);
        }
    });
})(jQuery);