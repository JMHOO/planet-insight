
from flask import Flask, abort, request
import json
from ..storage import DBInstanceLog

app = Flask(__name__)


@app.route('/')
def show_info():
    return 'Welcome to Insights!'


@app.route('/monitor/<instance_name>', methods=['POST'])
def accept_training_monitor(instance_name):
    if not request.json:
        abort(400)

    remote_log = DBInstanceLog(instance_name)
    remote_log.append('train', json.dumps(request.json))
    return 'instance name {}, data: {}'.format(instance_name, json.dumps(request.json))


def start_agent_service(port=9000):
    app.run(host='0.0.0.0', port=port)
