from .storage import DBJobInstance
import docker
import platform
import threading
from random import randint
from time import sleep
from simple_settings import LazySettings
import os


settings = LazySettings('insight.applications.settings')


class LocalDockerRunner():
    def __init__(self, cli, gpu_count, image_name, volumes, commands, environments=None):
        self.docker = cli
        self.gpu_count = gpu_count
        self.image_name = image_name
        self.volumes = volumes
        self.commands = commands
        self.environments = environments
        self.containerId = ""
        self._t = None
        self.volumes = {"nvidia_driver_375.82": "/usr/local/nvidia"}

    def start(self):
        self._t = threading.Thread(target=self.run_container)
        self._t.start()

    def is_container_running(self):
        for container in self.docker.containers(all=False):
            if container['Id'] == self.containerId:
                return True
        return False

    def __del__(self):
        if self._t:
            self._t.join()

    def run_container(self):
        commands = ''
        if self.commands:
            commands = 'bash -c "' + self.commands + '"'

        binds = []
        for s, d in self.volumes.items():
            binds.append(s + ":" + d)
        volumes = list(self.volumes.values())
        
        devices = ["/dev/nvidiactl:/dev/nvidiactl", "/dev/nvidia-uvm:/dev/nvidia-uvm"]
        for i in range(self.gpu_count):
            devices.append("/dev/nvidia{}:/dev/nvidia{}".format(i, i))
        host_config = self.docker.create_host_config(devices=devices, binds=binds)

        response = self.docker.create_container(
            image=self.image_name, 
            volumes=volumes, 
            command=commands, 
            environment=self.environments, 
            host_config=host_config)

        if response['Warnings'] is None:
            self.containerId = response['Id']
        else:
            print(response['Warnings'])
            return

        self.docker.start(self.containerId)

        print('Container {} started, waiting to finish...'.format(self.containerId))
        # Keep running until container is exited
        while self.is_container_running():
            sleep(1)

        # Remove the container when it is finished
        self.docker.remove_container(self.containerId)
        print('Container exited')


class AgentService(threading.Thread):
    def __init__(self, gpu_count=1):
        super().__init__()
        self.stoprequest = threading.Event()
        self.gpu_count = gpu_count

    def stop(self, timeout=None):
        self.stoprequest.set()
        super().join(timeout)

    def run(self):
        print('Agent service running...')
        try:
            aws_key = os.environ['AWS_ACCESS_KEY_ID']
            aws_access = os.environ['AWS_SECRET_ACCESS_KEY']
            aws_region = os.environ['AWS_DEFAULT_REGION']
        except KeyError:
            print('AWS credential not configed, exit.')
            return

        # docker instance
        self._docker = None
        try:
            if platform.system() is 'Windows':
                self._docker = docker.APIClient(base_url='npipe:////./pipe/docker_engine')
            else:
                self._docker = docker.APIClient(base_url='unix:///var/run/docker.sock')
        except:
            self._docker = None

        if self._docker is None:
            print('No docker engine installed, abort!')
            return

        print('connected to docker engine.')

        self._jobs = DBJobInstance()

        while not self.stoprequest.is_set():
            random_sleep = randint(3, 10)
            
            # do job checking
            new_job = self._jobs.check_new_job()
            if new_job is not None:
                print('Got new jog: {}'.format(new_job))
                pretrain_weights = new_job['pretrain']
                #if pretrain_weights != 'NONE':
                #    pretrain_weights = '-w ' + pretrain_weights
                #else:
                #    pretrain_weights = ''

                monitor_service = settings.MONITOR['HOST'] + settings.MONITOR['PATH']

                command = '/home/root/insight/run_worker.sh -i {} -m {} {} -d {} -s {}'.format(
                    new_job['instance_name'], new_job['model_name'], pretrain_weights, new_job['dataset_name'], monitor_service
                )

                print(command)

                environment = {
                    'AWS_ACCESS_KEY_ID': aws_key,
                    'AWS_SECRET_ACCESS_KEY': aws_access,
                    'AWS_DEFAULT_REGION': aws_region
                }

                # do job and waiting
                runner = LocalDockerRunner(
                    self._docker,
                    self.gpu_count,
                    settings.DOCKER['IMAGE'] + ':' + settings.DOCKER['VERSION'],
                    volumes=None,
                    commands=command,
                    environments=environment
                )
                # since we already in a thread, call block function instead of start another thread
                runner.run_container()

            # sleep random seconds between 5 ~ 30
            print('No job, random waiting {} seconds'.format(random_sleep))
            sleep(random_sleep)

