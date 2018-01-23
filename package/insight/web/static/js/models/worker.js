var app = app || {};

(function() {
    'use strict';

    app.Worker = Backbone.Model.extend({
        defaults: {
            worker_name: '',
            current_status: '',
            last_seen: '',
            system_info: '',
            idle: '',
            status_color: '',
            remotely_controlled: false
        },

        _startWorker: function() {
            var model = this;
            var workerName = this.get("worker_name");

            if(workerName === undefined || !workerName.includes("_paperspace")) {
                return false;
            } else {
                var machineId = workerName.split('-')[1];
                if(machineId !== undefined) {
                    Backbone.ajax(_.extend({
                        url: "/insight/api/v1.0/workers/paperspace_start",
                        method: "POST",
                        data: JSON.stringify({"machineId": machineId}),
                        contentType: "application/json",
                        success: function() {
                            model.set("current_status", "running");
                        },
                        error: function(response) {
                            console.log(response);
                        }

                    }));
                }

            }
        },

        _stopWorker: function() {
            var model = this;
            var workerName = this.get("worker_name");

            if(workerName === undefined || !workerName.includes("_paperspace")) {
                return false;
            } else {
                var machineId = workerName.split('-')[1];
                if(machineId !== undefined) {
                    Backbone.ajax(_.extend({
                        url: "/insight/api/v1.0/workers/paperspace_stop",
                        method: "POST",
                        data: JSON.stringify({"machineId": machineId}),
                        contentType: "application/json",
                        success: function() {
                            model.set("current_status", "offline");
                        },
                        error: function(response) {
                            console.log(response);
                        }

                    }));
                }

            }
        }

    });
})();