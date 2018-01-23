var app = app || {};

app.WorkerView = Backbone.View.extend({
    tagName: 'tr',

    events: {
        'click .start-worker': '_startWorker',
        'click .stop-worker': '_stopWorker'
    },

    template: _.template($('#worker-template').html()),

    initialize: function() {
        this.render();
        this.listenTo(this.model, "change", this.render);
    },

    render: function() {
        var status_val = this.model.get("current_status");
        var status = "";
        if (status_val === "training") {
            status = "badge badge-pill badge-warning";
        } else if (status_val === "idle") {
            status = "badge badge-pill badge-success";
        } else if (status_val === "offline") {
            status = "badge badge-pill badge-secondary";
        }
        this.model.set("status_color", status);
        this.model.set("remotely_controlled", this._isRemotelyControlled(this.model.get("worker_name")));
        this.$el.html(this.template(this.model.attributes));
        return this
    },

    _isRemotelyControlled: function(workerName) {
        return workerName.includes("_paperspace");
    },

    _startWorker: function(e) {
        e.preventDefault();
        this.model._startWorker();
    },

    _stopWorker: function(e) {
        e.preventDefault();
        this.model._stopWorker();
    }
});