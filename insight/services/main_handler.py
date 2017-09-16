
from flask import Flask, abort, request
import json

app = Flask(__name__)


@app.route('/')
def show_info():
    return 'Welcome to Insights!'


@app.route('/monitor/<modelname>', methods=['POST'])
def accept_training_monitor(modelname):
    if not request.json:
        abort(400)

    return 'model name {}, data: {}'.format(modelname, json.dumps(request.json))


def start_service(port=9000):
    app.run(port=port)