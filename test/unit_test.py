import os
import json
from insight.translate import Convert
from keras.models import model_from_json


def TestMain():
    keras_json = test_json_translate()
    test_keras_model_build(keras_json)


def test_json_translate():
    c = Convert(target="keras")
    json_file = os.path.join(os.getcwd(), 'test/example2.json')
    keras_json = c.parser(json_file)
    print(json.dumps(json.loads(keras_json), sort_keys=True, indent=4))
    return keras_json


def test_keras_model_build(keras_json):
    model = model_from_json(keras_json)
    print(model.summary())
    model_json = model.to_json()
    with open("model_rebuild.json", "w") as json_file:
        json_file.write(model_json)


if __name__ == "__main__":
    TestMain()
