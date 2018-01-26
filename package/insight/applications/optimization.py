"""
optimization.py

Hyperparameter optimization

author: Ryan Reece <ryan.reece@cern.ch>
created: Jan 23, 2018
"""

import argparse
from insight.optimizer import optimize


#______________________________________________________________________________
def options():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', '--instance', dest='instance_name', help="Job instance name")
#    parser.add_argument('-m', '--model', dest='model_name', help='Model defination')
#    parser.add_argument('-w', '--weights', dest='pretrained_model', help="pretrained model weights file of s3 bucket")
#    parser.add_argument('-d', '--dataset', dest='training_dataset', help="training dataset objetct of s3 bucket")
#    parser.add_argument('-s', '--service', dest='monitor_service', help="service that monitor training")
    parser.add_argument('-p', '--hparams', dest='hparams', help="hyperparameter dictionary", default=None)
    args = parser.parse_args()
#    if args.instance_name is None or args.model_name is None or args.training_dataset is None or args.monitor_service is None:
#        parser.print_help()
#        exit()
    return args


#______________________________________________________________________________
def main():
    args = options()

#    space = {
#        'conv2/filters' : ('ci', [16, 32, 64]),
#        'conv4/filters' : ('ci', [64, 128, 256]),
#        'dropout2/rate' : ('cf', [0.25, 0.50]),
#        'dense1/units' :  ('ci', [256, 512, 1024]),
#        'dropout3/rate' : ('cf', [0.25, 0.50]),
#        }

    space = '{"conv2/filters" : ["ci", [16, 32, 64]], "dropout2/rate" : ["cf", [0.25, 0.50]]}'
    optimize(name='reece-test', space=space, model_name='CNN-Base', epochs=5, max_jobs=3)


