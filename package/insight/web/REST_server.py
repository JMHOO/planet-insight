import json
import os
import re
import argparse
from datetime import datetime, timedelta
from functools import wraps
from flask import abort, request, send_from_directory, redirect
from flask_api import FlaskAPI
from flask_httpauth import HTTPBasicAuth
from insight.storage import AWSResource, DBInstanceLog
from insight.builder import Convert


# global AWS resource
aws = AWSResource()

# flask application
app = FlaskAPI(__name__, static_folder='static')
auth = HTTPBasicAuth()


def checkAWS(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not aws.has_credential:
            abort(400)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/base')
def base_root():
    return app.send_static_file('base.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


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
GET	    /insight/api/v1.0/models	            Retrieve list of models
GET	    /insight/api/v1.0/models/[model_name]	Retrieve a model
POST    /insight/api/v1.0/models                Create a new model
PUT	    /insight/api/v1.0/models/[model_name]	Update an existing model
DELETE  /insight/api/v1.0/models/[model_name]	Delete a model
'''


@app.route('/insight/api/v1.0/models', methods=["GET"])
#@auth.login_required
@checkAWS
def list_models():
    models = []
    all_models = aws.models.list()
    for item in all_models:
        models.append({"model_name": item["model_name"], "model_defination": item["model_defination"]})
    return models  #{"models": models}


@app.route('/insight/api/v1.0/models/<model_name>', methods=["GET", "PUT", "DELETE"])
@checkAWS
def retrieve_model(model_name):
    if request.method == 'PUT':
        if not request.json:
            abort(400)
        aws.models.update(model_name, request.json['defination'])
        return {"model": request.json['defination']}
    elif request.method == "DELETE":
        aws.models.delete(model_name)
        return {"result": True}
    else:
        json_model = aws.models.get(model_name)
        return {"model": json_model}


@app.route('/insight/api/v1.0/models', methods=['POST'])
@checkAWS
def create_model():
    if not request.json or 'name' not in request.json:
        abort(400)

    model_name = request.json['name']
    model_defination = request.json['defination']

    # convert keras json to our json format if necessary
    c = Convert()
    model_defination = c.toInsightJson(model_defination)

    aws.models.put(model_name, model_defination)
    return {"model_name": model_name, "model_defination": model_defination}, 201


'''
GET	    /insight/api/v1.0/jobs	                    Retrieve list of jobs
GET	    /insight/api/v1.0/jobs/[instance_name]	    Retrieve a job instance
POST    /insight/api/v1.0/jobs                        Create a new job
PUT	    /insight/api/v1.0/jobs/[instance_name]	    Update an existing job
DELETE  /insight/api/v1.0/jobs/[instance_name]	    Delete a job
GET	    /insight/api/v1.0/jobs/[instance_name]/logs   Retrieve the logs of a job
'''


@app.route('/insight/api/v1.0/jobs', methods=["GET"])
#@auth.login_required
@checkAWS
def list_jobs():
    jobs = []
    all_jobs = aws.tasks.list()
    for item in all_jobs:
        timestamp = datetime.fromtimestamp(float(item['created']))
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
        item['created'] = timestamp
        jobs.append(item)
    return jobs  # {"jobs": jobs}


@app.route('/insight/api/v1.0/jobs/<instance_name>', methods=["GET", "PUT", "DELETE"])
@checkAWS
def retrieve_job(instance_name):
    if request.method == 'PUT':
        if not request.json:
            abort(400)
        aws.tasks.update(instance_name, request.json['defination'])
        return {"model": request.json['defination']}
    elif request.method == "DELETE":
        db_log = DBInstanceLog(instance_name)
        db_log.clear()
        aws.tasks.delete(instance_name)
        return {"result": True}
    else:
        job = aws.tasks.get(instance_name)
        if job:
            timestamp = datetime.fromtimestamp(float(job['created']))
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
            job['created'] = timestamp
        return {"job": job}


@app.route('/insight/api/v1.0/jobs', methods=['POST'])
@checkAWS
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
    aws.tasks.new_job(internal_json)
    timestamp = datetime.fromtimestamp(float(internal_json['created']))
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
    internal_json['created'] = timestamp
    return internal_json, 201


@app.route('/insight/api/v1.0/jobs/<instance_name>/logs', methods=["GET"])
@checkAWS
def fetch_job_logs(instance_name):
    db_log = DBInstanceLog(instance_name)
    logs = db_log.fetch()
    return logs


'''
GET	    /insight/api/v1.0/datasets	                    Retrieve list of datasets
POST    /insight/api/v1.0/datasets/upload                 Upload a dataset
DELETE  /insight/api/v1.0/datasets/[dataset_name]	        Delete a dataset

GET	    /insight/api/v1.0/weights                         Retrieve list of trained models
POST    /insight/api/v1.0/weights/upload                  Upload a dataset
DELETE  /insight/api/v1.0/weights/[weights_file]          Delete a trained models
GET     /insight/api/v1.0/weights/[weights_file]          Download a trained models
'''



@app.route('/insight/api/v1.0/datasets', methods=["GET"])
#@auth.login_required
@checkAWS
def list_datasets():
    files = []
    all_file = aws.datasets.list()
    for f in all_file:
        if not f['name'].endswith('/'):
            files.append(f)
    return files


@app.route('/insight/api/v1.0/dataset-paired', methods=["GET"])
#@auth.login_required
@checkAWS
def list_paired_datasets():
    files = []
    all_file = aws.datasets.list()
    for f in all_file:
        if not f['name'].endswith('/'):
            files.append(f)

    train, test = [], []
    pattern = re.compile('(?:^|[a-zA-Z0-9\/-]*)([-]train|[-]test)')
    for obj in files:
        match = pattern.search(obj['name'])
        if not match:
            continue
        elif '-train' in match.group():
            train.append(obj)
        elif '-test' in match.group():
            test.append(obj)

    if len(train) != len(test) or len(train) == 0:
        return files

    files = []
    for i in range(len(train)):
        files.append({
            'name': train[i]['name'].split("-train")[0],
            'train_size': train[i]['size'],
            'test_size': test[i]['size']
        })

    return files


@app.route('/insight/api/v1.0/weights', methods=["GET"])
#@auth.login_required
@checkAWS
def list_results():
    files = []
    all_file = aws.results.list()
    for f in all_file:
        if not f['name'].endswith('/'):
            files.append(f)
    return files


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
@checkAWS
def upload_dataset():
    return _upload_to_s3(request.files, aws.datasets)


@app.route('/insight/api/v1.0/weights/upload', methods=['POST'])
@checkAWS
def upload_weights():
    return _upload_to_s3(request.files, aws.results)


@app.route('/insight/api/v1.0/datasets/<dataset_name>', methods=["GET", "DELETE"])
@checkAWS
def delete_dataset(dataset_name):
    if request.method == "DELETE":
        aws.datasets.delete(dataset_name)
        return {"result": True}
    elif request.method == "GET":
        return {"file": dataset_name}


@app.route('/insight/api/v1.0/weights/<weights_file>', methods=["GET", "DELETE"])
@checkAWS
def delete_weights_file(weights_file):
    if request.method == "DELETE":
        aws.results.delete(weights_file)
        return {"result": True}
    elif request.method == "GET":
        url = aws.results.presigned_url(weights_file)
        return redirect(url)


'''
GET	    /insight/api/v1.0/workers             Retrieve list of active instances
POST    /insight/api/v1.0/workers/report      report a worker's status
'''


@app.route('/insight/api/v1.0/workers', methods=["GET"])
@checkAWS
def list_workers():
    workers = []
    dtNow = datetime.now()
    max_idle_minutes = timedelta(minutes=3)
    all_workers = aws.workers.list()
    for item in all_workers:
        timestamp = datetime.fromtimestamp(float(item['last_seen']))
        idle_span = dtNow - timestamp
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        item['last_seen'] = timestamp

        item['idle'] = str(idle_span)
        if idle_span > max_idle_minutes:
            item['current_status'] = 'offline'

        workers.append(item)
    return workers


@app.route('/insight/api/v1.0/workers/report', methods=["POST"])
@checkAWS
def report_worker():
    if not request.json or \
       'name' not in request.json or \
       'status' not in request.json:
        abort(400)

    if 'system_info' in request.json:
        system_info = request.json["system_info"]
    else:
        system_info = '{}'

    internal_json = {
        "name": request.json["name"],
        "status": request.json["status"],
        "info": system_info
    }
    aws.workers.report(internal_json['name'], system_info, internal_json['status'])
    return {"result": True}


'''
POST    /insight/api/v1.0/credentials              Store AWS credential
'''


@app.route('/insight/api/v1.0/credentials', methods=["POST"])
def write_credentials():
    if not request.json or \
       'access_key' not in request.json or \
       'secret_key' not in request.json or \
       'region' not in request.json:
        abort(400)

    default_config = os.path.expanduser("~/.aws/credentials")
    with open(default_config, "w") as fp:
        fp.write('[default]\n')
        fp.write('aws_access_key_id = {}\n'.format(request.json['access_key']))
        fp.write('aws_secret_access_key = {}\n'.format(request.json['secret_key']))
        fp.write('region = {}\n'.format(request.json['region']))

    # recreate aws resource
    global aws
    aws = AWSResource(access_key=request.json['access_key'], secret_key=request.json['secret_key'], region=request.json['region'])

    return {"result": True}


def start_agent_service():
    cmdParser = argparse.ArgumentParser(description='')
    cmdParser.add_argument('-p', '--port', dest='port', help="RESTful server port")
    args = cmdParser.parse_args()
    port = 9000 if not args.port else args.port
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    start_agent_service()
