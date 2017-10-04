var app = app || {};

app.JSONModelView = Backbone.View.extend({
    tagName: 'div',
    className: 'col',

    events: {
        'click .removemodel': 'removeModel',
    },

    render: function() {
        //var context = $('<div/>').addClass("col");
        var thumbnail = $('<div/>').addClass("card");
        var header = $('<div/>').addClass("card-header").text(this.model.get("model_name"));
        var body = $('<div/>').addClass("card-body");
        //var title = $('<h3/>').addClass("card-title").text(this.model.get("model_name"));
        var json_def = $('<p/>').addClass("card-text")
            .append($('<pre/>').addClass("pre-scrollable").append($('<code/>').addClass("hljs json").html(
                JSON.stringify(JSON.parse(this.model.get("model_defination")), null, 2)
            )));
        //var json_def = $('<p/>').addClass("card-text").append(renderjson.set_icons('˖', '﹘').set_show_to_level(1)(JSON.parse(this.model.get('model_defination'))));
        var op_button = $('<p/>').html('<a href="#" class="btn btn-danger removemodel" role="button">Remove</a>');

        body.append(json_def).append(op_button)

        thumbnail.append(header).append(body);
        //context.append(thumbnail);

        this.$el.append(thumbnail);

        // $('pre code').each(function(i, block) {
        //     hljs.highlightBlock(block);
        // });

        return this;
    },

    removeModel: function() {
        console.log(this.model.get("model_name"));
        this.model.destroy();
    },
});