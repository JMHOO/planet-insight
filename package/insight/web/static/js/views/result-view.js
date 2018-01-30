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

        this.log_collection = new app.TaskLogs(this.model.get('instance_name'));

        // Load the Visualization API and the corechart package.
//        google.charts.load('current', {'packages':['corechart']});
      google.charts.load('current', {'packages':['line']});

        // Set a callback to run when the Google Visualization API is loaded.
        google.charts.setOnLoadCallback(drawChart);

        var that = this;

        // Callback that creates and populates a data table,
        // instantiates the pie chart, passes in the data and
        // draws it.
        function drawChart() {
	        var data = new google.visualization.DataTable();

      	    data.addColumn('number', 'Epoch');
      	    data.addColumn('number', 'Training Loss');
      	    data.addColumn('number', 'Testing Loss');

            var i = 0;
            that.log_collection.fetch({
                success: function() {
                    that.log_collection.each(function(log) {
                        if (log.get('train')) {
                            var train_log = log.get('train');
//                            data.addRow([train_log.epoch, train_log.loss, train_log.val_loss]);
                            data.addRow([i, 0.5, i*0.4]);
                            i++;
                        }
                    }, that);
                }
            });

      		var options = {
      		  chart: {
      		    title: 'Loss vs epoch',
//      		    subtitle: 'in millions of dollars (USD)'
      		  },
      		  width: 600,
      		  height: 500
      		};
//            var chart = new google.visualization.LineChart(document.getElementById('result_chart'));
//            chart.draw(data, options);

          var chart = new google.charts.Line(document.getElementById('result_chart'));
          chart.draw(data, google.charts.Line.convertOptions(options));
        }

//        // Load the Visualization API and the corechart package.
//        google.charts.load('current', {'packages':['corechart']});
//
//        // Set a callback to run when the Google Visualization API is loaded.
//        google.charts.setOnLoadCallback(drawChart);

//        // Callback that creates and populates a data table,
//        // instantiates the pie chart, passes in the data and
//        // draws it.
//        function drawChart() {
//
//        // Create the data table.
//        var data = new google.visualization.DataTable();
//        data.addColumn('string', 'Topping');
//        data.addColumn('number', 'Slices');
//        data.addRows([
//          ['Mushrooms', 3],
//          ['Onions', 1],
//          ['Olives', 1],
//          ['Zucchini', 1],
//          ['Pepperoni', 2]
//        ]);
//
//        // Set chart options
//        var options = {'title':'How Much Pizza I Ate Last Night',
//                       'width':400,
//                       'height':300};
//
//        // Instantiate and draw our chart, passing in some options.
//        var chart = new google.visualization.PieChart(document.getElementById('result_chart'));
//        chart.draw(data, options);
//        }

        $('#view-result-dialog').modal();
        $('#view-result-dialog').modal('handleUpdate');
    },
});
