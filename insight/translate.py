import json
import os


class Convert(object):
    def __init__(self, target="keras"):
        self._target = target
        self._json_file = None
        self._inherit_from = None

    def parser(self, json_file):
        parsed_json = None
        with open(json_file, 'r') as fp:
            self._json_file = json_file
            j = json.load(fp)
            if self._target == 'keras':
                parsed_json = self._parser_keras(j)
        return parsed_json

    def _parser_keras(self, j):
        # inherit json
        if isinstance(j, list) and isinstance(j[0], dict) and 'From' in j[0]:
            print(self._json_file)
            json_from_file = os.path.join(os.path.dirname(self._json_file), j[0]['From'] + '.json')
            if not os.path.exists(json_from_file):
                print('{} file doesn\'t exist'.format(json_from_file))
                return None
            
            with open(json_from_file, 'r') as fp:
                self._inherit_from = json.load(fp)

        if self._inherit_from is not None:
            # merge two json files
            j = self._merge_json(self._inherit_from, j)

        seq = KerasSequential()
        if isinstance(j, list):
            for sub_json in j:
                seq.config += KerasObject.Translate(sub_json)
        elif isinstance(j, dict):
            seq.config += KerasObject.Translate(j)
        return seq.toJSON()

    def _merge_json(self, original, divergence):
        for layer in divergence:
            if isinstance(layer, dict) and 'From' in layer:
                continue

            for key in layer:
                layer_config = layer[key]
                # no name property in layer, ignore change
                if 'name' in layer_config:
                    target_name = layer_config['name']
                    for ol in original:
                        for ol_key in ol:
                            if 'name' in ol[ol_key] and ol[ol_key]['name'] == target_name:
                                ol[ol_key] = layer_config
                                ol[ol_key]['trainable'] = True
                            else:
                                ol[ol_key]['trainable'] = False

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
                    self.config[key] = KerasObject.Translate(config[key])[0]
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toDict(self):
        return self.__dict__

    @staticmethod
    def Translate(json_obj):
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
