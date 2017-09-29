var app = app || {};

app.DatasetView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#dataset-template').html()),

    events: {
        'click .remove-dataset': 'removeDataset'
    },

    initialize: function() {
        this.render();
    },

    render: function() {
        this.$el.html(this.template(this.model.attributes));
        return this
    },

    removeDataset: function() {
        console.log(this.model.get("name"));
        this.model.destroy();
    },
});