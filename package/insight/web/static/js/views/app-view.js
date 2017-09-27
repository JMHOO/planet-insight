var app = app || {};

(function($) {
    'use strict';
    // The Application
    // ---------------

    // Our overall **AppView** is the top-level piece of UI.
    app.AppView = Backbone.View.extend({

        // Instead of generating a new element, bind to the existing skeleton of
        // the App already present in the HTML.
        el: '.insightapp',

        // At initialization we bind to the relevant events on the `Todos`
        // collection, when items are added or changed. Kick things off by
        // loading any preexisting todos that might be saved in *localStorage*.
        initialize: function() {

            this.$json_models = this.$('.json_models');

            this.listenTo(app.models, 'add', this.addOne);
            this.listenTo(app.models, 'reset', this.addAll);
            this.listenTo(app.models, 'change:completed', this.filterOne);
            this.listenTo(app.models, 'filter', this.filterAll);
            this.listenTo(app.models, 'all', _.debounce(this.render, 0));

            // Suppresses 'add' events with {reset: true} and prevents the app view
            // from being re-rendered for every model. Only renders when the 'reset'
            // event is triggered at the end of the fetch.
            //app.todos.fetch({ reset: true });
        },

        // Re-rendering the App just means refreshing the statistics -- the rest
        // of the app doesn't change.
        render: function() {
            var json_models = [
                { name: 'cnn1', defination: '[{12121}]' },
                { name: 'cnn2', defination: '[{12121}]' },
            ];
            model_list = new app.ModelsView(json_models);

            this.$json_models.append(model_list.render().el);
            this.$json_models.show();
        }
    });
})(jQuery);