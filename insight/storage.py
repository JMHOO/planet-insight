import boto3
import botocore
import uuid


class DynamoDB(object):
    def __init__(self, table_name='insight-models'):
        self._dynamodb = boto3.resource('dynamodb')
        self._model_table = self._dynamodb.Table(table_name)

    def _put(self, item_dict):
        self._model_table.put_iten(
            Item=item_dict
        )

    def _get(self, keyname, keyvalue):
        return self._model_table.get_item(
            Key={keyname: keyvalue}
        )


class DBInsightModels(DynamoDB):
    def __init__(self):
        super().__init__(self, table_name='insight-models')

    def put(self, key, json_str):
        self._put({
            'model_name': key, 'model_defination': json_str
        })

    def get(self, key):
        item = self._get('model_name', key)['Item']
        return item['model_defination']


class DBJobInstance(DynamoDB):
    def __init__(self):
        super().__init__(self, table_name='job-instance')

    def put(self):
        pass

    def get(self, instance_name):
        item = self._get('instance_name', instance_name)['Item']
        return {'name': item['instance_name'], 'dataset': item['dataset_name'], 'weights': item['weights']}

    '''
        entity is a dictionary, e.g.:
        {
            name = cnn1-cifar-10,    # instance name
            dataset = cifar-10,      # object name of S3
            weights = cnn1-cifar-10, # pre-trained weight, set to None if train from scratch
        }
    '''
    def new_job(self, entity):
        if not isinstance(entity, dict):
            return None

        uid = uuid.uuid4().hex
        entity['id'] = uid
        if entity['name'] is not None:
            # check the unique of instance name
            if self._get('instance_name', entity['name']) is not None:
                print('instance-name already existed!')
                return

            self._put({
                'instance_name': entity['name'], 'dataset_name': entity['dataset'], 'weights': entity['weights']
            })


class S3DB(object):
    def __init__(self, bucket_name):
        s3_client = boto3.client('s3')
        self._bucket = None

        self._s3 = boto3.resource('s3')
        # check if the bucket existed or not
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            self._bucket = self._s3.Bucket(bucket_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print('bucket not exist')

    def upload(self, obj_name, local_file_name):
        if not self._bucket:
            return False

        self._bucket.upload_file(local_file_name, obj_name)

    def download(self, obj_name, local_filename):
        if not self._bucket:
            return None

        try:
            self._bucket.download_file(obj_name, local_filename)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")

    def create_folder(self, folder_path):
        if folder_path[-1] is not '/':
            folder_path = folder_path + '/'
        self._bucket.put_object(Key=folder_path)

    