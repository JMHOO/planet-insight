var app = app || {};

app.ResultView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#result-template').html()),

    events: {
        'click .viewresult': 'viewResult',
//        'click .remove-result': 'removeResult'
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
        } else if (status_val == "preparing") {
            status = "badge badge-pill badge-secondary";
        }
        this.model.set("status_color", status);

        this.$el.html(this.template(this.model.attributes));
        return this
    },

    removeResult: function() {
        console.log(this.model.get("model_name"));
        this.model.destroy();
    },

    viewResult: function(e) {
        var instance_name = this.model.get('instance_name');
        var result_body = $('#result-body').html('');
        result_body.append($('<h3/>').addClass("text-primary").text(this.model.get('instance_name')))
            .append($('<p/>').addClass("card-text")
                .append($('<p/>').html(
                    'Use model: ' + this.model.get('model_name') +
                    ' ----- Max Epochs: ' + this.model.get('epochs') +
                    '<br/>' + 'Dataset: ' + this.model.get('dataset_name') +
                    '<br/>' + 'Status: ' + this.model.get('job_status')
                )));
        //.append($('<p/>').text('Dataset: ' + this.model.get('dataset_name')))
        //.append($('<p/>').text('Status: ' + this.model.get('job_status'))));
        var result_logs = $('#result-logs').html('');
        //var result_logs_group = $('<ul/>').addClass('list-group');
        var result_logs_group = $('<pre/>'); //.addClass('list-group');
        result_logs.append(result_logs_group);

        this.log_collection = new app.TaskLogs(this.model.get('instance_name'));

        // Load the Visualization API and the corechart package.
        google.charts.load('current', {'packages':['line']});

        // Set a callback to run when the Google Visualization API is loaded.
        google.charts.setOnLoadCallback(drawChart);

        // Callback that creates and populates a data table,
        // instantiates the pie chart, passes in the data and
        // draws it.
        function drawChart() {

			var data = new google.visualization.DataTable();
      		data.addColumn('number', 'Epoch');
      		data.addColumn('number', 'Training Loss');
      		data.addColumn('number', 'Testing Loss');

            var that = this;
            this.log_collection.fetch({
                success: function() {
                    var output = '';
                    that.log_collection.each(function(log) {
                        if (log.get('train')) {
                            var train_log = log.get('train');
                            data.addRow([train_log.epoch, train_log.loss, train_log.val_loss]);
                        } else if (log.get('info')) {
                            output += log.get('info');
                        }
                        output += '\n';
                    }, that);
                    result_logs_group.append(output);
                }
            });

      		var options = {
      		  chart: {
      		    title: 'Loss vs epoch',
//      		    subtitle: 'in millions of dollars (USD)'
      		  },
      		  width: 500,
      		  height: 500
      		};

      		var chart = new google.charts.Line(document.getElementById('result_chart'));

      		chart.draw(data, google.charts.Line.convertOptions(options));
        }

        $('#view-result-dialog').modal();
        $('#view-result-dialog').modal('handleUpdate');
    },
});
