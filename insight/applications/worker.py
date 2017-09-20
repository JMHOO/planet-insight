import argparse
import os
import json
from insight.storage import DBJobInstance, DBInsightModels, DBInstanceLog, S3DB
from insight.builder import Convert
from simple_settings import LazySettings

settings = LazySettings('insight.applications.settings')



'''
    This is the main entry point of docker container
'''


def start_pipeline():
    # startup parameters parsering
    cmdParser = argparse.ArgumentParser(description='')
    cmdParser.add_argument('-i', '--instance', dest='instance_name', help="Job instance name")
    cmdParser.add_argument('-m', '--model', dest='model_name', help='Model defination')
    cmdParser.add_argument('-w', '--weights', dest='pretrained_model', help="pretrained model weights file of s3 bucket")
    cmdParser.add_argument('-d', '--dataset', dest='training_dataset', help="training dataset objetct of s3 bucket")
    args = cmdParser.parse_args()
    if args.instance_name is None or args.model_name is None or args.training_dataset is None:
        cmdParser.print_help()
        exit()

    #settings = json.loads(os.environ['APP_SETTINGS'])
    # fetch JSON model from central DB
    db_model = DBInsightModels()
    original_json = db_model.get({'model_name': args.model_name})

    conv = Convert()
    parent_json = conv.check_inheritance(original_json)
    if parent_json is not None:
        parent_json = db_model.get({'model_name': parent_json})

    # download weights file if required
    if args.pretrained_model is not None:
        s3_results = S3DB(bucket_name=settings.S3_BUCKET['RESULTS'])
        s3_results.download(args.pretrained_model, './{}.weights'.format(args.model_name))
        
    keras_model = conv.parser(original_json, parent_json)
    print(keras_model.summary())

    # download dataset
    s3_dataset = S3DB(bucket_name=settings.S3_BUCKET['DATASET'])
    s3_dataset.download(args.training_dataset, './{}.tar.gz'.format(args.model_name))

    # load dataset

    
    # training



if __name__ == "__main__":
    start_pipeline()
