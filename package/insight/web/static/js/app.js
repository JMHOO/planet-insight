var app = app || {};
var ENTER_KEY = 13;
var ESC_KEY = 27;

$(function() {
    'use strict';

    // kick things off by creating the `App`
    //new app.AppView();
    new app.JSONModelsListView();
    new app.TaskListView();
});