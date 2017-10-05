var app = app || {};

app.WeightsView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#weights-template').html()),

    events: {
        'click .remove-dataset': 'removeWeights'
    },

    initialize: function() {
        this.render();
    },

    render: function() {
        this.$el.html(this.template(this.model.attributes));
        return this
    },

    removeWeights: function() {
        console.log(this.model.get("name"));
        this.model.destroy();
    },
});