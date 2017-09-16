import boto3


class JsonModelDB(object):
    def __init__(self):
        self._dynamodb = boto3.resource('dynamodb')
        self._model_table = self._dynamodb.Table('insight-models')

    def put(self, name, json_str):
        self._model_table.put_item(
            Item={'model_name': name, 'model_defination': json_str}
        )

    def get(self, name):
        response = self._model_table.get_item(
            Key={'model_name': name}
        )
        item = response['Item']
        return item['model_defination']