
from flask import Flask, abort, request
import json

app = Flask(__name__)


@app.route('/')
def show_info():
    return 'Welcome to Insights!'


@app.route('/monitor/<instance_name>', methods=['POST'])
def accept_training_monitor(instance_name):
    if not request.json:
        abort(400)

    return 'instance name {}, data: {}'.format(instance_name, json.dumps(request.json))


def start_service(port=9000):
    app.run(port=port)