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
from insight.paperspace import Paperspace
from insight.optimizer import optimize


# global AWS resource
aws = AWSResource()

# global Paperspace resource
paperspace = Paperspace()

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


@app.route('/about')
def about_root():
    return app.send_static_file('about.html')


@app.route('/base')
def base_root():
    return app.send_static_file('base.html')


@app.route('/aboutme')
def aboutme():
    return redirect("https://about.me/ryan.reece", code=302)


@app.route('/slides')
def slides():
    return redirect("https://docs.google.com/presentation/d/1GN00stPnvaWol_g2n2b39-NJRXoTFTdEcS82-fFpL14/edit?usp=sharing", code=302)


@app.route('/slidespdf')
def slidespdf():
    return app.send_static_file("media/HYPR-AI-Ryan-Reece.pdf")


@app.route('/github')
def github():
    return redirect("https://github.com/rreece/hypr-ai", code=302)


@app.route('/rreece')
def ryan():
    return redirect("http://rreece.github.io/", code=302)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)


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
POST    /insight/api/v1.0/hyperjobs
'''

@app.route('/insight/api/v1.0/hyperjobs', methods=['POST'])
@checkAWS
def create_hyper_job():
    if not request.json or \
       'instance_name' not in request.json or \
       'model_name' not in request.json or \
       'dataset_name' not in request.json or \
       'epochs' not in request.json or \
       'hspace' not in request.json:
        abort(400)

    if 'pretrain' in request.json:
        weights = request.json["pretrain"]
    else:
        weights = "NONE"

    name = request.json["instance_name"]
    hspace = request.json["hspace"]
    model_name = request.json["model_name"]
    epochs = int(request.json["epochs"])
    dataset_name = request.json["dataset_name"]
    ## build hyperparams dictionary from user given string
    json_acceptable_string =  str(hspace).replace("'", "\"")
    hspace = json.loads(json_acceptable_string) # hspace is now a dict
    max_jobs = 25 # TODO HACK
    optimize(name=name, space=hspace, model_name=model_name, dataset_name=dataset_name, epochs=epochs, max_jobs=max_jobs)
    return hspace, 201


'''
GET     /insight/api/v1.0/results
'''

@app.route('/insight/api/v1.0/results', methods=['GET'])
@checkAWS
def list_results():
    jobs = []
    all_jobs = aws.tasks.list()
    for item in all_jobs:
        ## fix created timestamp
        timestamp = datetime.fromtimestamp(float(item['created']))
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
        item['created'] = timestamp
        ## add log metrics to job dict
        instance_name = item['instance_name']
        db_log = DBInstanceLog(instance_name)
        logs = db_log.fetch()
        loss = None
        best_loss = 1e99
        best_val_loss = 1e99
        best_acc = -1.0
        best_val_acc = -1.0
        best_epoch = -1
        last_epoch = -1
        for log in logs:
            if 'train' in log:
                metrics = log['train']
                assert 'loss' in metrics
                assert 'epoch' in metrics
                loss  = metrics['loss']
                val_loss  = metrics['val_loss']
                acc = metrics['acc']
                val_acc = metrics['val_acc']
                last_epoch = metrics['epoch'] + 1 # switch from 0-first to 1-first numbering
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_loss = loss
                    best_acc = acc
                    best_val_acc = val_acc
                    best_epoch = last_epoch
        if loss is not None:
            item['best_epoch'] = best_epoch
            item['best_loss']  = best_loss
            item['best_acc']   = best_acc
            item['best_val_loss']  = best_val_loss
            item['best_val_acc']   = best_val_acc
            item['best_epoch_str'] = '%i / %i' % (best_epoch, last_epoch)
            item['best_loss_str'] = '%.5g / %.5g' % (loss, val_loss)
            item['best_acc_str'] = '%.5g / %.5g' % (acc, val_acc)
        else:
            item['best_epoch'] = 0
            item['best_loss']  = 0
            item['best_acc']   = 0
            item['best_val_loss']  = 0
            item['best_val_acc']   = 0
            item['best_epoch_str'] = ''
            item['best_loss_str'] = ''
            item['best_acc_str'] = ''
        jobs.append(item)
    return jobs

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
def list_weights():
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


@app.route('/insight/api/v1.0/datasets/<dataset_name>', methods=["GET"])
@checkAWS
def get_dataset(dataset_name):
    url = aws.datasets.presigned_url(dataset_name)
    return redirect(url)


@app.route('/insight/api/v1.0/datasets/<dataset_name>', methods=["DELETE"])
@checkAWS
def delete_dataset(dataset_name):
    aws.datasets.delete(dataset_name)
    return {"result": True}


@app.route('/insight/api/v1.0/weights/<weights_file>', methods=["GET"])
@checkAWS
def get_weights_file(weights_file):
    url = aws.results.presigned_url(weights_file)
    return redirect(url)


@app.route('/insight/api/v1.0/weights/<weights_file>', methods=["DELETE"])
@checkAWS
def delete_weights_file(weights_file):
    aws.results.delete(weights_file)
    return {"result": True}


'''
GET	    /insight/api/v1.0/workers                       Retrieve list of active instances
POST    /insight/api/v1.0/workers/report                report a worker's status
POST    /insight/api/v1.0/workers/paperspace_start      start paperspace worker
POST    /insight/api/v1.0/workers/paperspace_stop       stop paperspace worker
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


@app.route('/insight/api/v1.0/workers/paperspace_start', methods=["POST"])
def start_paperspace_worker():
    if not request.json or 'machineId' not in request.json:
        abort(400, 'missing parameter: machineId')

    machine_id = request.json['machineId']
    response = Paperspace.start_machine(machine_id)
    return response


@app.route('/insight/api/v1.0/workers/paperspace_stop', methods=["POST"])
def stop_paperspace_worker():
    if not request.json or 'machineId' not in request.json:
        abort(400, 'missing parameter: machineId')

    machine_id = request.json['machineId']
    response = Paperspace.stop_machine(machine_id)
    return response


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
