var app = app || {};

app.WorkerView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#worker-template').html()),

    initialize: function() {
        this.render();
    },

    render: function() {
        this.$el.html(this.template(this.model.attributes));
        return this
    },
});