var app = app || {};

app.WorkerView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#worker-template').html()),

    initialize: function() {
        this.render();
    },

    render: function() {
        var status_val = this.model.get("current_status");
        var status = "";
        if (status_val == "training") {
            status = "badge badge-pill badge-warning";
        } else if (status_val == "idle") {
            status = "badge badge-pill badge-success";
        } else if (status_val == "offline") {
            status = "badge badge-pill badge-secondary";
        }
        this.model.set("status_color", status);
        this.$el.html(this.template(this.model.attributes));
        return this
    },
});