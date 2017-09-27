var app = app || {};

app.JSONModelView = Backbone.View.extend({
    tagName: 'div',
    className: 'modelContainer1',
    template: _.template($('#model-template').html()),

    render: function() {
        var context = $('<div/>').addClass("col-md-6");
        var thumbnail = $('<div/>').addClass("thumbnail");
        var caption = $('<div/>').addClass("caption");
        var title = $('<h3/>').text(this.model.get("model_name"));
        var json_def = $('<p/>').append(renderjson.set_icons('˖', '﹘').set_show_to_level(1)(JSON.parse(this.model.get('model_defination'))));
        var op_button = $('<p/>').html('<a href="#" class="btn btn-danger" role="button">Remove</a>');

        caption.append(title).append(json_def).append(op_button)
        thumbnail.append(caption);
        context.append(thumbnail);

        this.$el.append(context);

        return this;
    }
});