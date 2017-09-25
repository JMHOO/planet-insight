import json
import os
from datetime import datetime
from flask import abort, request
from flask_api import FlaskAPI
from flask_httpauth import HTTPBasicAuth
from insight.storage import DBInstanceLog, DBInsightModels, DBJobInstance, S3DBDataset, S3DBResults

app = FlaskAPI(__name__)
auth = HTTPBasicAuth()
db_model = DBInsightModels()
db_jobs = DBJobInstance()
s3_dataset = S3DBDataset()
s3_results = S3DBResults()


@app.route('/')
def show_info():
    return {'Welcome': 'to Insights!'}


@app.route('/monitor/<instance_name>', methods=['GET', 'POST'])
def accept_training_monitor(instance_name):
    payload = request.form.get('data')
    try:
        data = json.loads(payload)
    except:
        return {'error': 'invalid payload'}

    remote_log = DBInstanceLog(instance_name)
    remote_log.append('train', data)
    # return 'instance name {}, data: {}'.format(instance_name, data)
    return {instance_name: data}


'''
GET	    http://insight-rest.umx.io/insight/api/v1.0/models	            Retrieve list of models
GET	    http://insight-rest.umx.io/insight/api/v1.0/models/[model_name]	Retrieve a model
POST    http://insight-rest.umx.io/insight/api/v1.0/models              Create a new model
PUT	    http://insight-rest.umx.io/insight/api/v1.0/models/[model_name]	Update an existing model
DELETE  http://insight-rest.umx.io/insight/api/v1.0/models/[model_name]	Delete a model
'''


@app.route('/insight/api/v1.0/models', methods=["GET"])
#@auth.login_required
def list_models():
    models = []
    all_models = db_model.list()
    for item in all_models:
        models.append({"model_name": item["model_name"], "model_defination": item["model_defination"]})
    return {"models": models}


@app.route('/insight/api/v1.0/models/<model_name>', methods=["GET", "PUT", "DELETE"])
def retrieve_model(model_name):
    if request.method == 'PUT':
        if not request.json:
            abort(400)
        db_model.update(model_name, request.json['defination'])
        return {"model": request.json['defination']}
    elif request.method == "DELETE":
        db_model.delete(model_name)
        return {"result": True}
    else:
        json_model = db_model.get(model_name)
        return {"model": json_model}
        

@app.route('/insight/api/v1.0/models/', methods=['POST'])
def create_model():
    if not request.json or 'name' not in request.json:
        abort(400)

    model_name = request.json['name']
    model_defination = request.json['defination']
    db_model.put(model_name, model_defination)
    return {"model": model_defination}, 201


'''
GET	    http://insight-rest.umx.io/insight/api/v1.0/jobs	                    Retrieve list of jobs
GET	    http://insight-rest.umx.io/insight/api/v1.0/jobs/[instance_name]	    Retrieve a job instance
POST    http://insight-rest.umx.io/insight/api/v1.0/jobs                        Create a new job
PUT	    http://insight-rest.umx.io/insight/api/v1.0/jobs/[instance_name]	    Update an existing job
DELETE  http://insight-rest.umx.io/insight/api/v1.0/jobs/[instance_name]	    Delete a job
GET	    http://insight-rest.umx.io/insight/api/v1.0/jobs/[instance_name]/logs   Retrieve the logs of a job
'''


@app.route('/insight/api/v1.0/jobs', methods=["GET"])
#@auth.login_required
def list_jobs():
    jobs = []
    all_jobs = db_jobs.list()
    for item in all_jobs:
        timestamp = datetime.fromtimestamp(float(item['created']))
        timestamp = timestamp.strftime('%Y-%m-%d %H:%m')
        item['created'] = timestamp
        jobs.append(item)
    return {"jobs": jobs}


@app.route('/insight/api/v1.0/jobs/<instance_name>', methods=["GET", "PUT", "DELETE"])
def retrieve_job(instance_name):
    if request.method == 'PUT':
        if not request.json:
            abort(400)
        db_jobs.update(instance_name, request.json['defination'])
        return {"model": request.json['defination']}
    elif request.method == "DELETE":
        db_log = DBInstanceLog(instance_name)
        db_log.clear()
        db_jobs.delete(instance_name)
        return {"result": True}
    else:
        job = db_jobs.get(instance_name)
        if job:
            timestamp = datetime.fromtimestamp(float(job['created']))
            timestamp = timestamp.strftime('%Y-%m-%d %H:%m')
            job['created'] = timestamp
        return {"job": job}


@app.route('/insight/api/v1.0/jobs', methods=['POST'])
def create_job():
    if not request.json or \
       'instance_name' not in request.json or \
       'model_name' not in request.json or \
       'dataset_name' not in request.json or \
       'epochs' not in request.json:
        abort(400)

    if 'pretrain' in request.json:
        weights = request.json["pretrain"]
    else:
        weights = "NONE"

    internal_json = {
        "job_status": "initial",
        "instance_name": request.json["instance_name"],
        "model_name": request.json["model_name"],
        "dataset_name": request.json["dataset_name"],
        "pretrain": weights,
        "epochs": request.json["epochs"]
    }
    db_jobs.new_job(internal_json)
    timestamp = datetime.fromtimestamp(float(internal_json['created']))
    timestamp = timestamp.strftime('%Y-%m-%d %H:%m')
    internal_json['created'] = timestamp
    return {"job": internal_json}, 201


@app.route('/insight/api/v1.0/jobs/<instance_name>/logs', methods=["GET"])
def fetch_job_logs(instance_name):
    db_log = DBInstanceLog(instance_name)
    logs = db_log.fetch()
    return {"logs": logs}


'''
GET	    http://insight-rest.umx.io/insight/api/v1.0/datasets	                    Retrieve list of datasets
POST    http://insight-rest.umx.io/insight/api/v1.0/datasets/upload                 Upload a dataset
DELETE  http://insight-rest.umx.io/insight/api/v1.0/datasets/[dataset_name]	        Delete a dataset

GET	    http://insight-rest.umx.io/insight/api/v1.0/weights                         Retrieve list of trained models
POST    http://insight-rest.umx.io/insight/api/v1.0/weights/upload                  Upload a dataset
DELETE  http://insight-rest.umx.io/insight/api/v1.0/weights/[weights_file]          Delete a trained models
'''



@app.route('/insight/api/v1.0/datasets', methods=["GET"])
#@auth.login_required
def list_datasets():
    files = []
    all_file = s3_dataset.list()
    for f in all_file:
        files.append(f)
    return {"objects": files}


@app.route('/insight/api/v1.0/weights', methods=["GET"])
#@auth.login_required
def list_results():
    files = []
    all_file = s3_results.list()
    for f in all_file:
        files.append(f)
    return {"objects": files}


def _upload_to_s3(files, s3_obj):
    # check if the post request has the file part
    if 'file' not in files:
        return {"error": "No file in the request"}
    file = files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if not file or file.filename == '':
        return {"error": "Empty file"}

    # filename = secure_filename(file.filename)
    filename = file.filename
    local_filename = os.path.join('./', filename)
    file.save("./" + filename)

    # upload to s3
    s3_obj.upload(filename, local_filename)
    # delete local file cache
    os.remove(local_filename)

    return {"file": filename}


@app.route('/insight/api/v1.0/datasets/upload', methods=['POST'])
def upload_dataset():
    return _upload_to_s3(request.files, s3_dataset)


@app.route('/insight/api/v1.0/weights/upload', methods=['POST'])
def upload_weights():
    return _upload_to_s3(request.files, s3_results)


@app.route('/insight/api/v1.0/datasets/<dataset_name>', methods=["DELETE"])
def delete_dataset(dataset_name):
    if request.method == "DELETE":
        s3_dataset.delete(dataset_name)
        return {"result": True}


@app.route('/insight/api/v1.0/weights/<weights_file>', methods=["DELETE"])
def delete_dataset(weights_file):
    if request.method == "DELETE":
        s3_results.delete(weights_file)
        return {"result": True}


def start_agent_service(port=9000):
    app.run(host='0.0.0.0', port=port)
