import os
import requests

PAPERSPACE_API_KEY = ''
CONFIG_HOST = 'https://api.paperspace.io'

if 'PAPERSPACE_API_KEY' in os.environ:
    PAPERSPACE_API_KEY = os.environ['PAPERSPACE_API_KEY']


class Paperspace():

    @staticmethod
    def start_machine(machine_id):
        http_method = 'POST'
        path = '/machines/' + machine_id + '/start'
        r = requests.request(http_method, CONFIG_HOST + path, headers={'x-api-key': PAPERSPACE_API_KEY})

        if r.status_code == 204:
            return {}
        else:
            return r.json()

    @staticmethod
    def stop_machine(machine_id):
        http_method = 'POST'
        path = '/machines/' + machine_id + '/stop'
        r = requests.request(http_method, CONFIG_HOST + path, headers={'x-api-key': PAPERSPACE_API_KEY})

        if r.status_code == 204:
            return {}
        else:
            return r.json()
