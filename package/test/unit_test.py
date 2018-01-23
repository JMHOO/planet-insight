import os
import json
import platform
from insight.builder import Convert
from insight.storage import S3DB, DBInsightModels, DBJobInstance, DBInstanceLog, DBWorker
from insight.applications import settings
from insight.agent import AgentService
from keras.models import model_from_json
from simple_settings import LazySettings
from keras.optimizers import *


def TestMain():
    # test_json_build_from_file()
    # keras_model = test_json_build_from_string()
    # print(type(keras_model))
    # print(keras_model.summary())
    # test_keras_model_build(keras_json)

    #test_json_build_from_file()
    # test_keras_json_from_file()
    # print(keras_model.summary())
    test_dynamodb()
    # test_s3()
    # test_agent()
    # test_worker_report()
    #test_save_keras_model()
    # test_optimizer_serizal()


def test_json_build_from_file():
    c = Convert()
    json_file = os.path.join(os.getcwd(), 'package/test/example.json')
    keras_model = c.parser(json_file)
    print(keras_model.summary())


def test_keras_json_from_file():
    c = Convert()
    json_file = os.path.join(os.getcwd(), 'package/test/keras_model.json')
    keras_model = c.parser(json_file)
    print(keras_model.summary())

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
        { "Dense": { "units": 10, "activation": "softmax", "name": "softmax1" } },
        { "Compiler": { "optimizer": "adam", "loss": "categorical_crossentropy", "metrics": ["accuracy"] } }
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
        { "Dense": { "units": 10, "activation": "softmax", "name": "softmax1" } },
        { "Compiler": { "optimizer": { "adam": {"lr": 0.001, "decay": 1e-6} }, "loss": "binary_crossentropy", "metrics": ["accuracy"] } } 
    ]
    '''

    converted_from_keras = '''[{"Convolution2D": {"dilation_rate": [1, 1], "activation": "relu", "dtype": "float32", "inputs": [null, 32, 32, 3], "kernel_regularizer": null, "bias_regularizer": null, "use_bias": true, "activity_regularizer": null, "trainable": true, "kernel_constraint": null, "kernel_initializer": {"VarianceScaling": {"seed": null, "distribution": "uniform", "mode": "fan_avg", "scale": 1}}, "padding": "valid", "name": "conv2d_1", "strides": [1, 1], "filters": 32, "kernel_size": [3, 3], "bias_constraint": null, "data_format": "channels_last"}}, {"Convolution2D": {"dilation_rate": [1, 1], "activation": "relu", "use_bias": true, "kernel_initializer": {"VarianceScaling": {"seed": null, "distribution": "uniform", "mode": "fan_avg", "scale": 1}}, "kernel_regularizer": null, "bias_regularizer": null, "activity_regularizer": null, "trainable": true, "kernel_constraint": null, "padding": "valid", "name": "conv2d_2", "strides": [1, 1], "filters": 64, "kernel_size": [3, 3], "bias_constraint": null, "data_format": "channels_last"}}, {"MaxPooling2D": {"trainable": true, "pool_size": [2, 2], "padding": "valid", "name": "max_pooling2d_1", "data_format": "channels_last", "strides": [2, 2]}}, {"Dropout": {"trainable": true, "name": "dropout_1", "rate": 0.25}}, {"Convolution2D": {"dilation_rate": [1, 1], "activation": "relu", "use_bias": true, "kernel_initializer": {"VarianceScaling": {"seed": null, "distribution": "uniform", "mode": "fan_avg", "scale": 1}}, "kernel_regularizer": null, "bias_regularizer": null, "activity_regularizer": null, "trainable": true, "kernel_constraint": null, "padding": "valid", "name": "conv2d_3", "strides": [1, 1], "filters": 256, "kernel_size": [3, 3], "bias_constraint": null, "data_format": "channels_last"}}, {"MaxPooling2D": {"trainable": true, "pool_size": [2, 2], "padding": "valid", "name": "max_pooling2d_2", "data_format": "channels_last", "strides": [2, 2]}}, {"Convolution2D": {"dilation_rate": [1, 1], "activation": "relu", "use_bias": true, "kernel_initializer": {"VarianceScaling": {"seed": null, "distribution": "uniform", "mode": "fan_avg", "scale": 1}}, "kernel_regularizer": null, "bias_regularizer": null, "activity_regularizer": null, "trainable": true, "kernel_constraint": null, "padding": "valid", "name": "conv2d_4", "strides": [1, 1], "filters": 128, "kernel_size": [3, 3], "bias_constraint": null, "data_format": "channels_last"}}, {"MaxPooling2D": {"trainable": true, "pool_size": [2, 2], "padding": "valid", "name": "max_pooling2d_3", "data_format": "channels_last", "strides": [2, 2]}}, {"Dropout": {"trainable": true, "name": "dropout_2", "rate": 0.25}}, {"Flatten": {"trainable": true, "name": "flatten_1"}}, {"Dense": {"activation": "relu", "use_bias": true, "kernel_initializer": {"VarianceScaling": {"seed": null, "distribution": "uniform", "mode": "fan_avg", "scale": 1}}, "bias_regularizer": null, "activity_regularizer": null, "units": 1024, "trainable": true, "kernel_constraint": null, "name": "dense_1", "kernel_regularizer": null, "bias_constraint": null}}, {"Dropout": {"trainable": true, "name": "dropout_3", "rate": 0.5}}, {"Dense": {"activation": "softmax", "use_bias": true, "kernel_initializer": {"VarianceScaling": {"seed": null, "distribution": "uniform", "mode": "fan_avg", "scale": 1}}, "bias_regularizer": null, "activity_regularizer": null, "units": 10, "trainable": true, "kernel_constraint": null, "name": "dense_2", "kernel_regularizer": null, "bias_constraint": null}}]'''

    optimizer_json = '''
    [
        { "From": "example" },
        {
            "input": "softmax1",
            "Compiler": { "optimizer": "sgd", "loss": "categorical_crossentropy", "metrics": ["accuracy"] }
        }
    ]
    '''

    c = Convert()
    #keras_model = c.parser(example_json)
    #keras_model = c.parser(cut_json, example_json)
    keras_model = c.parser(cut_json, example_json, hparams={"conv2/filters":32})
    #keras_model = c.parser(optimizer_json, example_json)
    print(keras_model)

    return keras_model


def test_keras_model_build(keras_json):
    model = model_from_json(keras_json)
    print(model.summary())
    model_json = model.to_json()
    with open("model_rebuild.json", "w") as json_file:
        json_file.write(model_json)


def test_dynamodb():
    
    # db_model = DBInsightModels()

#    example_json = '''[{
#        "Convolution2D": {"inputs": [null, 32, 32, 3],"filters": 32, "kernel_size": [3, 3],"strides": [1, 1],"activation": "relu","padding": "valid",
#            "kernel_initializer": {
#                "VarianceScaling": {"scale": 1,"mode": "fan_avg","distribution": "uniform"}
#            },"name": "conv1"}
#        },
#        { "Convolution2D": { "filters": 64, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv2" } },
#        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool1" } },
#        { "Dropout": { "rate": 0.25, "name": "dropout1" } },
#        { "Convolution2D": { "filters": 128, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv3" } },
#        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool2" } },
#        { "Convolution2D": { "filters": 128, "kernel_size": [3, 3], "strides": [1, 1], "activation": "relu", "padding": "valid", "name": "conv4" } },
#        { "MaxPooling2D": { "pool_size": [2, 2], "strides": [2, 2], "padding": "valid", "name": "pool3" } },
#        { "Dropout": { "rate": 0.25, "name": "dropout2" } },
#        { "Flatten": {} },
#        { "Dense": { "units": 1024, "activation": "relu", "name": "dense1" } },
#        { "Dropout": { "rate": 0.5, "name": "dropout3" } },
#        { "Dense": { "units": 10, "activation": "softmax", "name": "softmax1" } }
#    ]'''

    # json_db.put('example', example_json)
    # print(db_model.get('example'))

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
    log = DBInstanceLog('reece-test-05')
    # log.append('info', 'abc')
    # log.append('training', '{"epoch": 0, "val_loss": 0.993394958114624, "val_acc": 0.6555, "loss": 1.0491512520599364, "acc": 0.6309600000190735}')

    # test log block
    #for i in range(210):
    #    log.append('info', 'msg.{}'.format(i + 1))

    # test fetch
    print(log.fetch(fetch_all=True))

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

def test_save_keras_model():
    json_file = os.path.join(os.getcwd(), 'package/test/keras_model.json')
    with open(json_file, 'r') as fp:
        json_context = json.load(fp)
    #layers = _serizalize_layer(json_context['config'])
    #print(layers)
    layers = []
    for layer in json_context['config']:
        layers.append(_serizalize_layer(layer))
    print(json.dumps(layers))

def _serizalize_layer(layer):
    layer_json = []
    if not isinstance(layer, dict):
        return layer

    if 'class_name' in layer:
        config = layer['config']
        if isinstance(config, dict):
            sub_json = _serizalize_layer(config)
            if sub_json:
                layer_json.append({layer['class_name']: sub_json})
    else:
        keys_to_be_removed = []
        for k, v in layer.items():
            if isinstance(v, dict):
                sub_json = _serizalize_layer(v)
                if not sub_json:
                    keys_to_be_removed.append(k)
                    
                    #layer[k] = None
                else:
                    layer[k] = _serizalize_layer(v)
        for k in keys_to_be_removed:
            layer.pop(k, None)
        return layer

    if len(layer_json) == 1:
        return layer_json[0]

    return layer_json

def test_optimizer_serizal():
    a = Adam(lr=0.0001, decay=1e-6)
    print(serialize(a))

    print(serialize(Adam()))

if __name__ == "__main__":
    TestMain()
