var app = app || {};
var ENTER_KEY = 13;
var ESC_KEY = 27;

$(function() {
    'use strict';

    // kick things off by creating the `App`
    //new app.AppView();
    app.jsonlist = new app.JSONModelsListView();
    app.tasklist = new app.TaskListView();
    app.datasetlist = new app.DatasetListView();
    app.weightslist = new app.WeightsListView();
    app.clusterlist = new app.WorkerListView();
});