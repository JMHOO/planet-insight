$(document).ready(function() {

    $("#sidebar a").on("click", function() {
        $("#sidebar").find(".active").removeClass("active");
        $(this).parent().addClass("active");
        $(this).tab('show');
    });


    $("#btnNewModel").click(function() {
        $('#add-json-model').modal();
    });

    $("#btnNewTask").click(function() {
        // load dataset list
        $('#selectDataset').html('');
        $.ajax({
                url: '/insight/api/v1.0/dataset-paired',
                type: 'GET',
                dataType: 'json',
            })
            .done(function(data) {
                var output = '';
                $.each(data, function(index, el) {
                    output += '<option value="' + el.name + '">' + el.name + '</option>';
                });
                $('#selectDataset').append(output)
            });
        // load json model list
        $('#selectJsonModel').html('');
        $.ajax({
                url: '/insight/api/v1.0/models',
                type: 'GET',
                dataType: 'json',
            })
            .done(function(data) {
                var output = '';
                $.each(data, function(index, el) {
                    output += '<option value="' + el.model_name + '">' + el.model_name + '</option>';
                });
                $('#selectJsonModel').append(output)
            });
        // load weights list
        $('#selectWeights').html('');
        $('#selectWeights').append('<option value="NONE">NONE</option>');
        $.ajax({
                url: '/insight/api/v1.0/weights',
                type: 'GET',
                dataType: 'json',
            })
            .done(function(data) {
                var output = '';
                $.each(data, function(index, el) {
                    output += '<option value="' + el.name + '">' + el.name + '</option>';
                });
                $('#selectWeights').append(output)
            });
        $('#add-task-model').modal();
    });

    $("#addNewModel").click(function(e) {
        e.preventDefault();
        var formData = {};
        formData['name'] = $('#model-name').val();
        formData['defination'] = $('#model-json').val();

        ajax_new_model(formData);
    });

    $('#addNewTask').click(function(e) {
        e.preventDefault();
        var formData = {};
        formData['instance_name'] = $('#instance-name').val();
        formData['model_name'] = $('#selectJsonModel').val();
        formData['dataset_name'] = $('#selectDataset').val();
        formData['pretrain'] = $('#selectWeights').val();
        formData['epochs'] = $('#maximum-epoch').val();

        ajax_new_task(formData);
    });

    $('#btnSettings').click(function(e) {
        $('#add-aws-configure').modal();
    });

    $('#btnUploadWeights').click(function(e) {
        $('#file-upload-dialog').on('show.bs.modal', function(e) {
            myDropzone.options.url = "/insight/api/v1.0/weights/upload";
        }).on('hidden.bs.modal', function(e) {
            myDropzone.removeAllFiles();
        }).modal();
    });

    $('#btnUploadDatasets').click(function(e) {
        $('#file-upload-dialog').on('show.bs.modal', function(e) {
            myDropzone.options.url = "/insight/api/v1.0/datasets/upload";
        }).on('hidden.bs.modal', function(e) {
            myDropzone.removeAllFiles();
        }).modal();
    });

    $("#btnRefreshWeights").click(function(e) {
        app.weightslist.refresh();
    });

    $("#btnRefreshDatasets").click(function(e) {
        app.datasetlist.refresh();
    });

    $("#btnRefreshCluster").click(function(e) {
        app.clusterlist.refresh();
    });

    // load local json file
    $("#fileLocalJSON").on('change', function(e) {
        var filename = e.target.files[0];
        console.log(filename);
        var fileReader = new FileReader();
        fileReader.onload = function(fileLoadedEvent) {
            var textFromFileLoaded = fileLoadedEvent.target.result;
            $("#model-json").text(textFromFileLoaded);
        };
        fileReader.readAsText(filename, "UTF-8");
    });

    $("#saveAWSConfig").click(function(e) {
        var formData = {};
        formData['access_key'] = $('#aws-access-key').val();
        formData['secret_key'] = $('#aws-secret-key').val();
        formData['region'] = $('#aws-default-region').val();

        ajax_save_aws_configure(formData)
    });

    myDropzone = initialize_dropzone();

});

function ajax_new_model(options) {
    $.ajax({
        type: "POST",
        url: "/insight/api/v1.0/models",
        data: JSON.stringify(options),
        contentType: "application/json;",
        dataType: "json",
        success: function(data, status, jqXHR) {
            app.jsonlist.collection.add(data);
        },
        error: function(jqXHR, status) {
            console.log(jqXHR);
        }
    });
};

function ajax_new_task(options) {
    $.ajax({
        type: "POST",
        url: "/insight/api/v1.0/jobs",
        data: JSON.stringify(options),
        contentType: "application/json;",
        dataType: "json",
        success: function(data, status, jqXHR) {
            app.tasklist.collection.add(data);
        },
        error: function(jqXHR, status) {
            console.log(jqXHR);
        }
    });
};

function ajax_save_aws_configure(options) {
    $.ajax({
        type: "POST",
        url: "/insight/api/v1.0/credentials",
        data: JSON.stringify(options),
        contentType: "application/json;",
        dataType: "json",
        success: function(data, status, jqXHR) {
            location.reload();
        },
        error: function(jqXHR, status) {
            console.log(jqXHR);
        }
    });
};

function initialize_dropzone() {
    var previewNode = document.querySelector("#template");
    previewNode.id = "";
    var previewTemplate = previewNode.parentNode.innerHTML;
    previewNode.parentNode.removeChild(previewNode);

    var myDropzone = new Dropzone(document.body, { // Make the whole body a dropzone
        url: '/', // Set the url
        thumbnailWidth: 80,
        thumbnailHeight: 80,
        parallelUploads: 5,
        previewTemplate: previewTemplate,
        autoQueue: false, // Make sure the files aren't queued until manually added
        previewsContainer: "#previews", // Define the container to display the previews
        clickable: ".fileinput-button" // Define the element that should be used as click trigger to select files.
    });

    myDropzone.on("addedfile", function(file) {
        // Hookup the start button
        file.previewElement.querySelector(".start").onclick = function() {
            myDropzone.enqueueFile(file);
        };
    });

    // Update the total progress bar
    myDropzone.on("totaluploadprogress", function(progress) {
        document.querySelector("#total-progress .progress-bar").style.width = progress + "%";
    });

    myDropzone.on("sending", function(file) {
        // Show the total progress bar when upload starts
        document.querySelector("#total-progress").style.opacity = "1";
        // And disable the start button
        file.previewElement.querySelector(".start").setAttribute("disabled", "disabled");
    });

    // Hide the total progress bar when nothing's uploading anymore
    myDropzone.on("queuecomplete", function(progress) {
        document.querySelector("#total-progress").style.opacity = "0";
    });

    // Setup the buttons for all transfers
    // The "add files" button doesn't need to be setup because the config
    // `clickable` has already been specified.
    document.querySelector("#actions .start").onclick = function() {
        myDropzone.enqueueFiles(myDropzone.getFilesWithStatus(Dropzone.ADDED));
    };
    document.querySelector("#actions .cancel").onclick = function() {
        myDropzone.removeAllFiles(true);
    };

    return myDropzone;
};