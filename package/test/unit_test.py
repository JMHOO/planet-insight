import os
import json
import platform
from insight.builder import Convert
from insight.storage import S3DB, DBInsightModels, DBJobInstance, DBInstanceLog, DBWorker
from insight.applications import settings
from insight.agent import AgentService
from keras.models import model_from_json
from simple_settings import LazySettings


def TestMain():
    # keras_model = test_json_build_from_string() # test_json_build_from_file()
    # test_keras_model_build(keras_json)
    # print(keras_model.summary())
    # test_dynamodb()
    # test_s3()
    # test_agent()
    test_worker_report()


def test_json_build_from_file():
    c = Convert()
    json_file = os.path.join(os.getcwd(), 'test/example2.json')
    keras_json = c.parser(json_file)
    print(json.dumps(json.loads(keras_json), sort_keys=True, indent=4))
    return keras_json


def test_json_build_from_string():
    example_json = '''[{
        "Convolution2D": {"inputs": [null, 32, 32, 3],"filters": 32, "kernel_size": [3, 3],"strides": [1, 1],"activation": "relu","padding": "valid",
            "kernel_initializer": {
                "VarianceScaling": {"scale": 1,"mode": "fan_avg","distribution": "uniform"}
            },"name": "conv1"}
        },
        { "Convolution2D": { "filters": 64, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv2" } },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool1" } },
        { "Dropout": { "rate": 0.25, "name": "dropout1" } },
        { "Convolution2D": { "filters": 128, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv3" } },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool2" } },
        { "Convolution2D": { "filters": 128, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv4" } },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool3" } },
        { "Dropout": { "rate": 0.25, "name": "dropout2" } },
        { "Flatten": {} },
        { "Dense": { "units": 1024, "activation": "relu", "name": "dense1" } },
        { "Dropout": { "rate": 0.5, "name": "dropout3" } },
        { "Dense": { "units": 10, "activation": "softmax", "name": "softmax1" } }
    ]'''

    inherit_json = '''[
        { "From": "example_json" },
        { "Convolution2D": { "name": "conv3", "filters": 256, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid" } }
    ]'''

    cut_json = '''[
        { "From": "example_json" },
        { "Convolution2D": { "filters": 256, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv4" }, "input": "pool2" },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool3" } },
        { "Dropout": { "rate": 0.5, "name": "dropout2" } },
        { "Flatten": {} },
        { "Dense": { "units": 1024, "activation": "relu", "name": "dense1" } },
        { "Dropout": { "rate": 0.5, "name": "dropout3" } },
        { "Dense": { "units": 10, "activation": "softmax", "name": "softmax1" } }
    ]
    '''

    c = Convert()
    keras_model = c.parser(cut_json, example_json)
    return keras_model


def test_keras_model_build(keras_json):
    model = model_from_json(keras_json)
    print(model.summary())
    model_json = model.to_json()
    with open("model_rebuild.json", "w") as json_file:
        json_file.write(model_json)


def test_dynamodb():
    
    db_model = DBInsightModels()

    example_json = '''[{
        "Convolution2D": {"inputs": [null, 32, 32, 3],"filters": 32, "kernel_size": [3, 3],"strides": [1, 1],"activation": "relu","padding": "valid",
            "kernel_initializer": {
                "VarianceScaling": {"scale": 1,"mode": "fan_avg","distribution": "uniform"}
            },"name": "conv1"}
        },
        { "Convolution2D": { "filters": 64, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv2" } },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool1" } },
        { "Dropout": { "rate": 0.25, "name": "dropout1" } },
        { "Convolution2D": { "filters": 128, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv3" } },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool2" } },
        { "Convolution2D": { "filters": 128, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv4" } },
        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool3" } },
        { "Dropout": { "rate": 0.25, "name": "dropout2" } },
        { "Flatten": {} },
        { "Dense": { "units": 1024, "activation": "relu", "name": "dense1" } },
        { "Dropout": { "rate": 0.5, "name": "dropout3" } },
        { "Dense": { "units": 10, "activation": "softmax", "name": "softmax1" } }
    ]'''

    # json_db.put('example', example_json)
    print(db_model.get('example'))

    #jobInstances = DBJobInstance()
    # jobInstances.new_job({
    #     'name': 'cnn1-cifar-10-base',
    #     'dataset': 'dataset/cifar-10.tar.gz',
    #     'pretrain': 'NONE',
    #     'status': 'initial'
    # })
    # jobInstances.new_job({
    #     'name': 'cnn1-cifar-10-gen1',
    #     'dataset': 'dataset/cifar-10.tar.gz',
    #     'pretrain': 'models/cnn1-base.h5df',
    #     'status': 'training'
    # })
    #jobInstances.check_new_job()

    # log test
    # log = DBInstanceLog('cnn1-cifar-10-base')
    # log.append('info', 'abc')
    # log.append('training', '{"epoch": 0, "val_loss": 0.993394958114624, "val_acc": 0.6555, "loss": 1.0491512520599364, "acc": 0.6309600000190735}')

    # test log block
    #for i in range(210):
    #    log.append('info', 'msg.{}'.format(i + 1))

    # test fetch
    # print(log.fetch(fetch_all=True))

def test_s3():
    #s3 = S3DB('insight-results')
    # s3.create_folder('abc')
    #s3.upload('abc/a.txt', '/Users/Jimmy/Developer/insight/planet-insight/model_rebuild.json')
    #s3.download('abc/a.txt', '/Users/Jimmy/Downloads/model1.json')
    jobInstances = DBJobInstance()
    new_job = jobInstances.check_new_job()
    if new_job:
        print(new_job['dataset_name'])

        s3_dataset = S3DB(bucket_name=settings.S3_BUCKET['DATASET'])
        s3_dataset.download(new_job['dataset_name'], './{}.tar.gz'.format(new_job['instance_name']))

def test_agent():
    agent = AgentService()
    agent.start()
    agent.join()

def test_worker_report():
    db_w = DBWorker()
    db_w.report(platform.node(), system_info={'cpu': 4, 'memory': 16}, status='idle')


if __name__ == "__main__":
    TestMain()
