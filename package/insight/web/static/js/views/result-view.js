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
                result_logs_group.append(output);
            }
        });

        // Load the Visualization API and the corechart package.
        google.charts.load('current', {'packages':['line']});

        // Set a callback to run when the Google Visualization API is loaded.
        google.charts.setOnLoadCallback(drawChart);

        // Callback that creates and populates a data table,
        // instantiates the pie chart, passes in the data and
        // draws it.
        function drawChart() {
			var data = new google.visualization.DataTable();
      		data.addColumn('number', 'Day');
      		data.addColumn('number', 'Guardians of the Galaxy');
      		data.addColumn('number', 'The Avengers');
      		data.addColumn('number', 'Transformers: Age of Extinction');

      		data.addRows([
      		  [1,  37.8, 80.8, 41.8],
      		  [2,  30.9, 69.5, 32.4],
      		  [3,  25.4,   57, 25.7],
      		  [4,  11.7, 18.8, 10.5],
      		  [5,  11.9, 17.6, 10.4],
      		  [6,   8.8, 13.6,  7.7],
      		  [7,   7.6, 12.3,  9.6],
      		  [8,  12.3, 29.2, 10.6],
      		  [9,  16.9, 42.9, 14.8],
      		  [10, 12.8, 30.9, 11.6],
      		  [11,  5.3,  7.9,  4.7],
      		  [12,  6.6,  8.4,  5.2],
      		  [13,  4.8,  6.3,  3.6],
      		  [14,  4.2,  6.2,  3.4]
      		]);

      		var options = {
      		  chart: {
      		    title: 'Box Office Earnings in First Two Weeks of Opening',
      		    subtitle: 'in millions of dollars (USD)'
      		  },
      		  width: 900,
      		  height: 500
      		};

      		var chart = new google.charts.Line(document.getElementById('result_chart'));

      		chart.draw(data, google.charts.Line.convertOptions(options));
        }

        $('#view-result-dialog').modal();
        $('#view-result-dialog').modal('handleUpdate');
    },
});
