import json
import os
from keras.models import model_from_json, Model
from keras.layers import *
from keras.optimizers import Adam


class Convert(object):
    def __init__(self):
        self._json_file = None
        self._inherit_from = None

    def parser(self, json_or_file, inherit_from=None, weights_file=None):
        keras_model = None
        j = None
        if os.path.exists(json_or_file):
            with open(json_or_file, 'r') as fp:
                self._json_file = json_or_file
                j = json.load(fp)
        else:
            try:
                j = json.loads(json_or_file)
            except:
                j = None

        if j:
            keras_model = self._parser_keras(j, inherit_from)
            # use adam for test now
            keras_model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.0001, decay=1e-6), metrics=['accuracy'])
        return keras_model

    def check_inheritance(self, json_content):
        if isinstance(json_content, list) and isinstance(json_content[0], dict) and 'From' in json_content[0]:
            return json_content[0]['From']

        return None

    def _parser_keras(self, j, inherit_from=None, weights_file=None):
        model = None
        # inherit json
        cut_from = ""
        if isinstance(j, list) and isinstance(j[0], dict) and 'From' in j[0]:
            if self._json_file is not None:
                if not os.path.exists(inherit_from):
                    print('{} file doesn\'t exist'.format(inherit_from))
                    return None

                with open(inherit_from, 'r') as fp:
                    self._inherit_from = json.load(fp)
            else:
                self._inherit_from = json.loads(inherit_from)

            if j[1] is not None and isinstance(j[1], dict):
                for key in j[1]:
                    if key == "input":  # cut_from
                        cut_from = j[1][key]
                        break

        if self._inherit_from is not None:
            # determine cut parent network or just override
            if cut_from:
                # initialize parent model first, then load weights, then cut network
                model_parent = model_from_json(self._to_keras_json_model(self._inherit_from))
                if weights_file is not None:
                    model_parent.load_weights(weights_file, by_name=True)

                for layer in model_parent.layers:
                    layer.trainable = False     # freeze all layers in parent model

                point_layer = model_parent.get_layer(cut_from)
                model = self._join_model(model_parent, point_layer, j)
            else:
                # merge two json files, then create model from json directly
                j = self._merge_keras_json(self._inherit_from, j)
                model = model_from_json(j)
        else:
            model = self._to_keras_json_model(j)
            model = model_from_json(model)
        return model

    def _join_model(self, model_parent, point_layer, additional_json):
        module_objects = globals()
        tensor_start = point_layer.output
        end_layer = None
        for layer in additional_json:
            if isinstance(layer, dict) and 'From' in layer:
                continue
            
            layer_json = KerasObject.Build(layer)[0]

            keras_class = module_objects.get(layer_json['class_name'])
            if keras_class is None:
                raise ValueError('Unknown ' + layer_json['class_name'])

            inputs = tensor_start if end_layer is None else end_layer
            end_layer = keras_class.from_config(layer_json['config'])(inputs)

        return Model(inputs=model_parent.input, outputs=end_layer)

    def _to_keras_json_model(self, json_model):
        # check if already keras json
        if isinstance(json_model, dict) and 'keras_version' in json_model:
            return json.dumps(json_model)   # keras json, no need for conversion

        seq = KerasSequential()
        if isinstance(json_model, list):
            for sub_json in json_model:
                seq.config += KerasObject.Build(sub_json)
        elif isinstance(json_model, dict):
            seq.config += KerasObject.Build(json_model)
        return seq.toJSON()
        
    def _merge_keras_json(self, original, divergence):
        for new_layer in divergence:
            if isinstance(new_layer, dict) and 'From' in new_layer:
                continue

            for key in new_layer:
                new_layer_config = new_layer[key]
                # no name property in layer, ignore change
                if 'name' in new_layer_config:
                    target_name = new_layer_config['name']
                    for layer in original:
                        for kk in layer:
                            if 'name' in layer[kk] and layer[kk]['name'] == target_name:
                                layer[kk] = new_layer_config
                                layer[kk]['trainable'] = True
                            else:
                                layer[kk]['trainable'] = False

        return original


class KerasObject(object):
    CLASS_NAME_TABLE = {
        'Convolution2D': 'Conv2D',
        'MaxPooling2D': 'MaxPooling2D',
        'Dropout': 'Dropout',
        'Flatten': 'Flatten',
        'Dense': 'Dense',
        'VarianceScaling': 'VarianceScaling',
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
                    self.config[key] = KerasObject.Build(config[key])[0]
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toDict(self):
        return self.__dict__

    @staticmethod
    def Build(json_obj):
        configs = []
        if isinstance(json_obj, dict):
            for key in json_obj:
                if key in KerasObject.CLASS_NAME_TABLE:
                    configs.append(KerasObject(KerasObject.CLASS_NAME_TABLE[key], json_obj[key]).toDict())
                else:
                    configs.append(json_obj)
        else:
            configs.append(json_obj)
        return configs


class KerasSequential(KerasObject):
    def __init__(self):
        self.class_name = 'Sequential'
        self.keras_version = '2.0.8'
        self.backend = 'tensorflow'
        self.config = []
