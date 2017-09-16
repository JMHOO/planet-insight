import os
import json
from insight.builder import Convert
from insight.storage import JsonModelDB
from keras.models import model_from_json


def TestMain():
    # keras_model = test_json_build_from_string() # test_json_build_from_file()
    # test_keras_model_build(keras_json)
    # print(keras_model.summary())
    test_dynamodb()


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
    json_db = JsonModelDB()

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

    #json_db.put('example', example_json)
    json_db.get('example')


if __name__ == "__main__":
    TestMain()
