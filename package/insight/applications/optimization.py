"""
optimization.py

Hyperparameter optimization

author: Ryan Reece <ryan.reece@cern.ch>
created: Jan 23, 2018
"""

import argparse
import os
import json
from simple_settings import LazySettings
import subprocess
import math
import time

import numpy as np
np.random.seed(777) # for DEBUG

#import pickle
#from urllib.parse import urlparse
#from keras.callbacks import RemoteMonitor, ModelCheckpoint, EarlyStopping
#from keras.utils import to_categorical
#import keras.backend as K

from insight.storage import DBJobInstance, DBInsightModels, DBInstanceLog, S3DB
from insight.builder import Convert

settings = LazySettings('insight.applications.settings')

path_of_this_file = os.path.abspath( __file__ )
dir_of_this_file = os.path.dirname(os.path.abspath( __file__ ))


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

#    wait_for_job_to_finish('reece-')

#    job_inst_db = DBJobInstance()
#    job_instances = job_inst_db.list()
#    print(job_instances)
#    print(job_instances[0]['job_status'])

#    job_name = args.instance_name
#    remote_log = DBInstanceLog(job_name)
#    logs = remote_log.fetch(True)
#    loss = get_loss(job_name)
#    print('loss = %5g' % loss) # DEBUG

    space = {
        'conv2/filters' : ('s', [16, 32, 64]),
        }
    optimize(name='reece-test-alpha', space=space, max_jobs=3) # TODO

#    jobInstances = DBJobInstance()
#    jobInstances.new_job({
#        'instance_name': 'reece-test-11',
#        'dataset_name': 'dataset/cifar-10',
#        'epochs': '10',
#        'pretrain': 'NONE',
#        'model_name': 'CNN-Transfer',
#        'job_status': 'initial'
#    })

#    pretrain_weights = 'NONE'
#
#    monitor_service = settings.MONITOR['HOST'] + settings.MONITOR['PATH']
#    cmd = '{}/../../../run_worker.sh -i {} -m {} -w {} -d {} -s {}'.format(
#            dir_of_this_file,
#            new_job['instance_name'],
#            new_job['model_name'],
#            pretrain_weights, 
#            new_job['dataset_name'],
#            monitor_service
#            )
#
#    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
#    print(out)


#______________________________________________________________________________
def optimize(name, space, max_jobs=99):
    keys = list(space.keys())
    keys.sort()
    prev_hparams = list()
    prev_loss = list()
    for i_job, hps in enumerate(next_hyperparams(space, prev_hparams, prev_loss)):
        i_job = i_job+1 # start counting from 1 instead of 0
        print('step %i' % i_job) # DEBUG
        for k in keys:
            v = hps[k]
            print('%s = %5g' % (k, v)) # DEBUG
        job_name = '%s-%02i' % (name, i_job)
        job_ops = {
            'instance_name': job_name,
            'dataset_name': 'dataset/cifar-10',
            'epochs': '5', # TODO
            'pretrain': 'NONE',
            'model_name': 'CNN-Transfer',
            'job_status': 'initial' }
        ## TODO: add hyperparams to submit pass. understand the control of this loop!!!
        submit_job(job_ops)
        wait_for_job_to_finish(name) # HACK: waiting for all jobs to finish!!
        loss = get_loss(job_name)
        print('loss = %5g' % loss) # DEBUG
        prev_hparams.append(hps)
        prev_loss.append(loss)
        if i_job >= max_jobs-1:
            break

    best_hparams, best_loss = calc_best_hyperparams(prev_hparams, prev_loss)
    keys = list(best_hparams.keys())
    keys.sort()
    print('best_hparams :') # DEBUG
    for k in keys:
        v = best_hparams[k]
        print('%s = %5g' % (k, v)) # DEBUG
    print('best_loss = %g' % best_loss) # DEBUG


#______________________________________________________________________________
def next_hyperparams(space, prev_hparams=None, prev_loss=None, n_workers=1):
    """
    hyperparameters generator
    """
    while True:
        _keys = list(space.keys())
        _keys.sort()
        new_hparams = dict()
        for _key in _keys:
            _val = None
            ts = space[_key][0]
            xi = space[_key][1]
            if ts.lower() == 'f': # floats
                _val = xi[0] + (xi[1] - xi[0])*np.random.rand()
            elif ts.lower() == 'i': # ints
                _val = np.random.random_integers(xi[0], xi[1])
            elif ts.lower() == 's': # list of strings or any "choice"
                _val = np.random.choice(xi)
            else:
                assert False
            new_hparams[_key] = _val
        yield new_hparams


#______________________________________________________________________________
def submit_job(job_ops):
    """
    db_job_inst.new_job({
        'instance_name': 'reece-test-11',
        'dataset_name': 'dataset/cifar-10',
        'epochs': '10',
        'pretrain': 'NONE',
        'model_name': 'CNN-Transfer',
        'job_status': 'initial'
    })
    """
    db_job_inst = DBJobInstance()
    db_job_inst.new_job(job_ops)


#______________________________________________________________________________
def wait_for_job_to_finish(job_prefix):
    """
    TODO
    """
#    print('wait_for_job_to_finish') # DEBUG
    job_inst_db = DBJobInstance()
    all_done = False
    while not all_done:
        time.sleep(3)
        job_instances = job_inst_db.list()
        if job_instances:
            incomplete = False
            for job in job_instances:
                if job['instance_name'].startswith(job_prefix):
#                    print(job['instance_name']) # DEBUG
                    if job['job_status'] != 'completed':
                        incomplete = True
#                        print('incomplete') # DEBUG
#                        print(job) # DEBUG
                        break
            all_done = not incomplete
        else:
            all_done = True
    
#    print('all done') # DEBUG
#    print(job_instances)
#    print(job_instances[0]['job_status'])



#______________________________________________________________________________
def get_loss(job_name):
    """
    Franke function
    https://github.com/sigopt/sigopt-python/blob/master/sigopt/examples/franke.py
    http://www.sfu.ca/~ssurjano/franke2d.html
    """

#    def franke_function(x, y):
#        return (
#          .75 * math.exp(-(9. * x - 2.) ** 2. / 4.0 - (9. * y - 2.) ** 2. / 4.0) +
#          .75 * math.exp(-(9. * x + 1.) ** 2. / 49.0 - (9. * y + 1.) / 10.0) +
#          .5 * math.exp(-(9. * x - 7.) ** 2. / 4.0 - (9. * y - 3.) ** 2. / 4.0) -
#          .2 * math.exp(-(9. * x - 4.) ** 2. - (9.0 * y - 7.) ** 2.)
#        )
#
#    x = hps['x']
#    y = hps['y']
#
#    loss = franke_function(x, y) 
#    time.sleep(1)

    remote_log = DBInstanceLog(job_name)
    logs = remote_log.fetch(True)
    min_loss = 1e99
    min_loss_epoch = -1
    for log in logs:
        if 'train' in log:
            metrics = log['train']
            assert 'loss' in metrics
            assert 'epoch' in metrics
            loss  = metrics['loss']
            epoch = metrics['epoch']
            if loss < min_loss:
                min_loss = loss
                min_loss_epoch = epoch

#    print('min_loss = %5g, epoch = %i' % (min_loss, min_loss_epoch)) # DEBUG
    return min_loss


#______________________________________________________________________________
def calc_best_hyperparams(hparams_list, loss_list):
    best_hparams = None
    best_loss = 1e99
    assert len(hparams_list) == len(loss_list)
    for hparams, loss in zip(hparams_list, loss_list):
        if loss < best_loss:
            best_loss = loss
            best_hparams = hparams
    return best_hparams, best_loss


#______________________________________________________________________________
if __name__ == "__main__":
    main()
