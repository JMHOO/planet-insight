import boto3
import botocore
import json
import os
from boto3.dynamodb.conditions import Attr
from simple_settings import LazySettings
from datetime import datetime
from decimal import Decimal
import tarfile
import shutil

settings = LazySettings('insight.applications.settings')


class DynamoDB(object):
    def __init__(self, table_name):
        self._dynamodb = boto3.resource('dynamodb')
        self._model_table = self._dynamodb.Table(table_name)

    def _put(self, item_dict):
        self._model_table.put_item(Item=item_dict)

    def _get(self, key):
        item = None
        try:
            item = self._model_table.get_item(Key=key)['Item']
        except botocore.exceptions.ClientError as e:
            print(e)
        except KeyError:
            pass
        return item

    def _update(self, key, update_exp, attr_values, condition_exp=None):
        if condition_exp is None:
            self._model_table.update_item(Key=key, UpdateExpression=update_exp, ExpressionAttributeValues=attr_values)
        else:
            self._model_table.update_item(Key=key, UpdateExpression=update_exp, ConditionExpression=condition_exp, ExpressionAttributeValues=attr_values)
           
    def _query(self, key_condition_exp):
        response = self._model_table.query(KeyConditionExpression=key_condition_exp)
        return response['Items']

    def _scan(self, filter=None):
        if filter is not None:
            response = self._model_table.scan(FilterExpression=filter)
        else:
            response = self._model_table.scan()
        return response['Items']


class DBInsightModels(DynamoDB):
    def __init__(self):
        super().__init__(table_name=settings.DynamoDB_TABLE['JSONModel'])

    def put(self, key, json_str):
        self._put({
            'model_name': key, 'model_defination': json_str
        })

    def get(self, key):
        item = self._get({'model_name': key})
        return item['model_defination'] if item else '{}'

    def list(self):
        items = self._scan(filter=None)
        return items


class DBInstanceLog(DynamoDB):
    MAX_LOG_PER_BLOCK = 200

    def __init__(self, instance_name):
        super().__init__(table_name=settings.DynamoDB_TABLE['InstanceLogs'])
        self._instance_name = instance_name
        self._msg_block = self._next_block(1)

    def append(self, type, message):
        self._msg_block = self._next_block(self._msg_block)

        key = self._instance_name + '.' + str(self._msg_block)
        item = self._get({'log_id': key})
        if item is None:
            item = {'log_id': key, 'message': '[]'}
            self._put(item)

        message_attr = json.loads(item['message'])
        message_attr.append({type: message})
        self._update(
            key={'log_id': key},
            update_exp='SET message = :m0',
            attr_values={':m0': json.dumps(message_attr)}
        )

    def fetch(self, fetch_all=False):
        message = []
        start_block = 1 if fetch_all else self._msg_block
        for i in range(start_block, self._msg_block + 1):
            key = self._instance_name + '.' + str(i)
            item = self._get({'log_id': key})
            json_messge = json.loads(item['message']) if item is not None else []
            message += json_messge
        return message

    def _next_block(self, block_index):
        key = self._instance_name + '.' + str(block_index)
        item = self._get({'log_id': key})
        if item is not None:
            message = json.loads(item['message'])
            if len(message) > DBInstanceLog.MAX_LOG_PER_BLOCK:
                return self._next_block(block_index + 1)
        return block_index


class DBJobInstance(DynamoDB):
    def __init__(self):
        super().__init__(table_name=settings.DynamoDB_TABLE['JobInstance'])

    def put(self):
        pass

    def get(self, instance_name):
        return self._get({'instance_name': instance_name})
        # return {'name': item['instance_name'], 'dataset': item['dataset_name'], 'pretrain': item['pretrain'], 'status': item['job_status']}

    def update_status(self, instance_name, from_, to_):
        self._update(
            key={'instance_name': instance_name},
            update_exp='SET job_status = :s1',
            condition_exp='job_status = :s0',
            attr_values={':s0': from_, ':s1': to_})

    '''
        entity is a dictionary, e.g.:
        {
            name = cnn1-cifar-10,    # instance name
            dataset = cifar-10,      # object name of S3
            pretrain = cnn1-cifar-10, # pre-trained weight, set to None if train from scratch
            status  = initial / training / completed
        }
    '''
    def new_job(self, entity):
        if not isinstance(entity, dict):
            return None

        if entity['name'] is not None:
            # check the unique of instance name
            if self._get({'instance_name': entity['name']}) is not None:
                print('instance-name already existed!')
                return

            time_stamp = datetime.now().isoformat()
            created = Decimal(str(datetime.now().timestamp()))
            # print(datetime.now().timestamp())

            self._put({
                'instance_name': entity['name'], 'created': created, #'timestamp': time_stamp,
                'dataset_name': entity['dataset'], 'pretrain': entity['pretrain'], 'job_status': entity['status'],
                'epochs': entity['epochs'], 'model_name': entity['model']
            })

    def check_new_job(self):
        items = self._scan(filter=Attr('job_status').eq('initial'))
        if len(items) > 0:
            # fetch one job
            new_job = items[0]
            print(new_job)

            print(self.get(new_job['instance_name']))
            # lock instance
            self.update_status(new_job['instance_name'], from_='initial', to_='training')
            return new_job

        return None

    def list(self):
        items = self._scan(filter=None)
        return items


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
            _extract_archive(local_filename)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")

    def create_folder(self, folder_path):
        if folder_path[-1] is not '/':
            folder_path = folder_path + '/'
        self._bucket.put_object(Key=folder_path)

    def list(self):
        objs = []
        for obj in self._bucket.objects.all():
            objs.append({"name": obj.key, "size": humanable_size(obj.size)})
        return objs


def _extract_archive(file_path, path='.'):
    if tarfile.is_tarfile(file_path):
        with tarfile.open(file_path) as archive:
            try:
                archive.extractall(path)
            except (tarfile.TarError, RuntimeError,
                    KeyboardInterrupt):
                if os.path.exists(path):
                    if os.path.isfile(path):
                        os.remove(path)
                    else:
                        shutil.rmtree(path)
                raise
        return True
    return False


def humanable_size(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
