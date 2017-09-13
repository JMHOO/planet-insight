#from keras import *
import json


class Convert(object):
    def __init__(self, target="keras"):
        self._target = target

    def parser(self, json_file):
        parsed_json = None
        j = json.load(json_file)
        if self._target == 'keras':
            parsed_json = self._parser_keras(j)
        return parsed_json

    def _parser_keras(self, j):
        seq = KerasSequential()
        if isinstance(j, list):
            for sub_json in j:
                seq.config += KerasObject.Translate(sub_json)
        elif isinstance(j, dict):
            seq.config += KerasObject.Translate(j)
        return seq.toJSON()


class KerasObject(object):
    CLASS_NAME_TABLE = {
        'Convolution2D': 'Conv2D',
        'MaxPooling2D': 'MaxPooling2D',
    }
    ALIAS_TABLE = {
        'inputs': 'batch_input_shape'
    }

    def __init__(self, class_name, config):
        self.class_name = class_name
        self.config = {}
        if isinstance(config, dict):
            for key in config:
                if key in KerasObject.CLASS_NAME_TABLE:
                    self.config[key] = KerasObject(KerasObject.CLASS_NAME_TABLE[key], config[key]).toDict()
                elif key in KerasObject.ALIAS_TABLE:
                    self.config[KerasObject.ALIAS_TABLE[key]] = config[key]
                else:
                    self.config[key] = config[key]
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toDict(self):
        return self.__dict__

    @staticmethod
    def Translate(json_obj):
        configs = []
        for key in json_obj:
            if key in KerasObject.CLASS_NAME_TABLE:
                configs.append(KerasObject(KerasObject.CLASS_NAME_TABLE[key], json_obj[key]).toDict())
            else:
                configs.append(json_obj)
        return configs


class KerasSequential(KerasObject):
    def __init__(self):
        self.class_name = 'Sequential'
        self.keras_version = '2.0.8'
        self.backend = 'tensorflow'
        self.config = []
