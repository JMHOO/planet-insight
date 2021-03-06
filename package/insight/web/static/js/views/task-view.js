var app = app || {};

app.TaskView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#task-template').html()),

    events: {
        'click .viewtask': 'viewTask',
        'click .remove-task': 'removeTask'
    },

    initialize: function() {
        this.render();
    },

    render: function() {
        var status_val = this.model.get("job_status");
        console.log(status_val);
        var status = "";
        if (status_val == "training") {
            status = "badge badge-pill badge-warning";
        } else if (status_val == "completed") {
            status = "badge badge-pill badge-success";
        } else if (status_val == "preparing" || status_val == "initial") {
            status = "badge badge-pill badge-secondary";
        }
        this.model.set("status_color", status);

        this.$el.html(this.template(this.model.attributes));
        return this
    },

    removeTask: function() {
        console.log(this.model.get("model_name"));
        this.model.destroy();
    },

    viewTask: function(e) {
        var instance_name = this.model.get('instance_name');
        var task_body = $('#task-body').html('');
        task_body.append($('<h3/>').addClass("text-primary").text(this.model.get('instance_name')))
            .append($('<p/>').addClass("card-text")
                .append($('<p/>').html(
                    'Use model: ' + this.model.get('model_name') +
                    ' ----- Max Epochs: ' + this.model.get('epochs') +
                    '<br/>' + 'Dataset: ' + this.model.get('dataset_name') +
                    '<br/>' + 'Status: ' + this.model.get('job_status')
                )));
        //.append($('<p/>').text('Dataset: ' + this.model.get('dataset_name')))
        //.append($('<p/>').text('Status: ' + this.model.get('job_status'))));
        var task_logs = $('#task-logs').html('');
        //var task_logs_group = $('<ul/>').addClass('list-group');
        var task_logs_group = $('<pre/>'); //.addClass('list-group');
        task_logs.append(task_logs_group);

        this.log_collection = new app.TaskLogs(this.model.get('instance_name'));

        var that = this;
        this.log_collection.fetch({
            success: function() {
                var output = '';
                that.log_collection.each(function(log) {
                    //var item = $('<li/>').addClass('list-group-item');
                    if (log.get('train')) {
                        var train_log = log.get('train');
                        var loss = '';
                        if (train_log.loss) { loss = ', LOSS: ' + train_log.loss.toFixed(5); }
                        var val_loss = '';
                        if (train_log.val_loss) { val_loss = ', VAL LOSS: ' + train_log.val_loss.toFixed(5); }
                        var acc = '';
                        if (train_log.acc) { acc = ', ACC: ' + train_log.acc.toFixed(5); }
                        var val_acc = '';
                        if (train_log.val_acc) { val_acc = ', VAL ACC: ' + train_log.val_acc.toFixed(5); }
                        var epoch = 'Epoch-' + String(train_log.epoch + 1);
                        message = epoch + acc + val_acc + loss + val_loss;
                        output += message;
                        //item.text(message);
                        //item.addClass('list-group-item-light');
                    } else if (log.get('info')) {
                        output += log.get('info');
                        //item.text(log.get('info'));
                        //item.addClass('list-group-item-info');
                    }
                    output += '\n';
                }, that);
                task_logs_group.append(output);
            }
        });
        $('#view-task-dialog').modal();
        $('#view-task-dialog').modal('handleUpdate');
    },
});
