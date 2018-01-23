import json
import os
from keras.models import model_from_json, Model
from keras.layers import *
from keras.optimizers import *


class Convert(object):
    def __init__(self):
        self._json_file = None
        self._inherit_from = None

    def parser(self, json_or_file, inherit_from=None, weights_file=None, hparams=None):
        keras_model = None
        j = self._load_json(json_or_file)
        if j:
            if hparams:
                self._find_and_replace_dict(j, hparams)
            keras_model = self._parser_keras(j, inherit_from, weights_file=weights_file)
            # use adam for test now
            #keras_model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.0001, decay=1e-6), metrics=['accuracy'])
        return keras_model

    def check_inheritance(self, json_content):
        json_content = json.loads(json_content)
        if isinstance(json_content, list) and isinstance(json_content[0], dict) and 'From' in json_content[0]:
            return json_content[0]['From']

        return None

    def toInsightJson(self, json_or_file):
        converted_json = json_or_file
        j = self._load_json(json_or_file)
        if j and self._is_keras_json(json_or_file):
            layers = []
            for layer in j['config']:
                layers.append(self._convert_keras_layer(layer))
            converted_json = json.dumps(layers)
        return converted_json
        
    def _load_json(self, json_or_file):
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
        return j

    def _convert_keras_layer(self, layer):
        ALIAS_TABLE = {
            'batch_input_shape': 'inputs',
            'Conv2D': 'Convolution2D'
        }

        layer_json = []
        if not isinstance(layer, dict):
            return layer

        if 'class_name' in layer:
            config = layer['config']
            if isinstance(config, dict):
                sub_json = self._convert_keras_layer(config)
                if sub_json:
                    class_name = layer['class_name']
                    class_name = ALIAS_TABLE[class_name] if class_name in ALIAS_TABLE else class_name
                    layer_json.append({class_name: sub_json})
        else:
            keys_to_be_removed = []
            for k, v in layer.items():
                if isinstance(v, dict):
                    sub_json = self._convert_keras_layer(v)
                    if not sub_json:
                        keys_to_be_removed.append(k)
                    else:
                        if k in ALIAS_TABLE:
                            layer[ALIAS_TABLE[k]] = sub_json
                            keys_to_be_removed.append(k)
                        else:
                            layer[k] = sub_json
            for k in keys_to_be_removed:
                layer.pop(k, None)
            return layer

        if len(layer_json) == 1:
            return layer_json[0]

        return layer_json

    def _parser_keras(self, j, inherit_from=None, weights_file=None):
        model = None
        optimizer = None
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
                model_parent, parent_compiler = self._to_keras_json_model(self._inherit_from)
                model_parent = model_from_json(model_parent)
                if weights_file is not None:
                    model_parent.load_weights(weights_file, by_name=True)
                    print('Loaded pretrained model: {}, all layer from parent model will be frozen.'.format(weights_file))
                    for layer in model_parent.layers:
                        layer.trainable = False     # freeze all layers in parent model

                point_layer = model_parent.get_layer(cut_from)
                model, sub_compiler = self._join_model(model_parent, point_layer, j)
                compiler = sub_compiler if sub_compiler else parent_compiler
                model = self._compile_model(model, compiler)
            else:
                # merge two json files, then create model from json directly
                j = self._merge_keras_json(self._inherit_from, j)
                model, compiler = self._to_keras_json_model(j)
                model = model_from_json(j)
                model = self._compile_model(model, compiler)
        else:
            model, compiler = self._to_keras_json_model(j)
            model = model_from_json(model)
            if weights_file is not None:
                model.load_weights(weights_file, by_name=True)
                print('Loaded pretrained model: {}'.format(weights_file))
            model = self._compile_model(model, compiler)
        return model

    def _join_model(self, model_parent, point_layer, additional_json):
        compiler = None
        module_objects = globals()
        tensor_start = point_layer.output
        end_layer = None
        for layer in additional_json:
            if isinstance(layer, dict) and 'From' in layer:
                continue

            if isinstance(layer, dict) and 'Compiler' in layer:
                compiler = layer
                continue
            
            layer_json = KerasObject.Build(layer)
            for l in layer_json:
                if 'class_name' in l and 'config' in l:
                    layer_json = l
                    break

            keras_class = module_objects.get(layer_json['class_name'])
            if keras_class is None:
                raise ValueError('Unknown ' + layer_json['class_name'])

            inputs = tensor_start if end_layer is None else end_layer
            end_layer = keras_class.from_config(layer_json['config'])(inputs)

        if end_layer is None:
            return model_parent, compiler
        
        return Model(inputs=model_parent.input, outputs=end_layer), compiler

    def _to_keras_json_model(self, json_model):
        # check if already keras json
        if isinstance(json_model, dict) and self._is_keras_json(json_model):
            return json.dumps(json_model)   # keras json, no need for conversion

        compiler = None
        seq = KerasSequential()
        if isinstance(json_model, list):
            for sub_json in json_model:
                if 'Compiler' in sub_json:
                    compiler = sub_json
                else:
                    seq.config += KerasObject.Build(sub_json)
        elif isinstance(json_model, dict):
            seq.config += KerasObject.Build(json_model)
        return seq.toJSON(), compiler
        
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

    def _is_keras_json(self, json_model):
        return 'keras_version' in json_model and 'backend' in json_model

    '''
    "optimizer": "adam"
    "optimizer": { "adam": {"lr": 0.001, "decay": 1e-6}}
    "metrics": ["accuracy"]
    '''
    def _compile_model(self, model, compiler):
        optimizer = 'adam'
        loss = 'categorical_crossentropy'
        metrics = ['accuracy']
        if compiler:
            if 'Compiler' in compiler:
                compiler = compiler['Compiler']

            if 'optimizer' in compiler:
                optimizer = compiler['optimizer']
                if isinstance(optimizer, dict):
                    name, config = optimizer.popitem()
                    config = {'class_name': name, 'config': config}
                    optimizer = deserialize(config)
            if 'loss' in compiler:
                loss = compiler['loss']
            if 'metrics' in compiler:
                metrics = compiler['metrics']

        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        return model

    def _find_and_replace_dict(self, j, hps):
        """
        TODO
        """
#        print(type(j))
#        print(type(hps))
#        print(hps)
        assert isinstance(j, dict) or isinstance(j, list)
        _j = j
        if isinstance(j, dict):
            _j = [j]
            
        hype_keys = list(hps.keys())
        hype_keys.sort()

        for hype_descr in hype_keys:
            hype_split = os.path.split(hype_descr)
            assert len(hype_split) == 2
            hype_cname = hype_split[0]
            hype_name = hype_split[1]
            hype_val = hps[hype_descr]
            for _json in _j:
                if isinstance(_json, dict) and 'name' in _json:
                    if _json['name'] == hype_cname:
                        assert hype_name in _json
                        _json[hype_name] = hype_val # edit hyperparameter value!
        return j
        

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
