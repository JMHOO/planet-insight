var app = app || {};

app.JSONModelView = Backbone.View.extend({
    tagName: 'div',
    className: 'modelContainer',
    template: _.template($('#model-template').html()),

    render: function() {
        //this.el is what we defined in tagName. use $el to get access to jQuery html() function
        this.$el.html(this.template(this.model.attributes));

        return this;
    }
});