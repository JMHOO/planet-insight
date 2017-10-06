var app = app || {};

app.JSONModelView = Backbone.View.extend({
    tagName: 'div',
    className: 'col-sm-6',

    events: {
        'click .removemodel': 'removeModel',
    },

    render: function() {
        var container = $("<div/>").addClass("menu-category list-group mb-2");
        var titlebar = $("<div/>").addClass("menu-category-name list-group-item layer-title text-light");
        var title = $("<div/>").addClass("col-sm-10").text(this.model.get("model_name"));
        var op_button = $('<a/>').addClass("btn btn-danger removemodel layer-item-btn").html('<i class="fa fa-trash" aria-hidden="true"></i>');

        // title.append(op_button);
        container.append(titlebar);
        titlebar.append($("<div/>").addClass("row").append(op_button).append(title));
        var item_template = $("<div/>").addClass("menu-item list-group-item");
        var network = JSON.parse(this.model.get("model_defination"));
        $.each(network, function(i, json_obj) {
            var first_key = Object.keys(json_obj)[0];
            var layer_config = json_obj[first_key];
            var name_val = "";
            if (layer_config.hasOwnProperty('name')) {
                name_val = " (" + layer_config['name'] + ") - ";
            }
            var properties = "";
            if (typeof(layer_config) == "object") {
                $.each(layer_config, function(key, val) {
                    if (key != "name") {
                        properties += " " + key + ": ";
                        if (typeof(val) == "object") {
                            properties += JSON.stringify(val);
                        } else {
                            properties += val;
                        }
                    }
                });
            } else {
                properties += ": " + layer_config;
            }

            raw_json = JSON.stringify(json_obj, null, 2);
            first_key = "<a class=\"text-primary\" data-toggle=\"tooltip\" data-placement=\"right\" data-html=\"false\" title='" + raw_json + "'>" + first_key + '</a>';
            //first_key = '<strong>' + first_key + '</strong>';
            var layer_text = first_key + name_val + properties;

            var layer_html = $("<div/>").addClass("list-group-item layer-item");

            layer_html.html(layer_text);
            container.append(layer_html);
        });
        this.$el.append(container);

        return this;
    },

    render1: function() {
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