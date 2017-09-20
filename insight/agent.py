from .storage import DBJobInstance
from .util.daemon import Daemon
import docker
import platform
import threading
from random import randint
from time import sleep
from simple_settings import LazySettings

settings = LazySettings('insight.applications.settings')


class LocalDockerRunner():
    def __init__(self, cli, image_name, volumes, commands, environments=None):
        self.docker = cli
        self.image_name = image_name
        self.volumes = volumes
        self.commands = commands
        self.environments = environments
        self.containerId = ""
        self._t = None

    def start(self):
        self._t = threading.Thread(target=self.run)
        self._t.start()

    def is_container_running(self):
        for container in self.containers(all=False):
            if container['Id'] == self._containerid:
                return True
        return False

    def __del__(self):
        if self._t:
            self._t.join()

    def run(self):
        commands = ''
        if self.commands:
            commands = 'bash -c "' + self.commands + '"'

        self.containerId = self.docker.create_container(image=self.image_name, command=commands)
        self.docker.start(self.containerId)

        # Keep running until container is exited
        while self.docker.container_running():
            sleep(1)

        # Remove the container when it is finished
        self.docker.remove_container(self.containerId)


class AgentService(Daemon):
    def run(self):
        self._jobs = DBJobInstance()
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

        while True:
            random_sleep = randint(5, 30)

            # do job checking
            new_job = self._jobs.check_new_job()
            if new_job is not None:
                # do job and waiting
                runner = LocalDockerRunner(
                    self._docker,
                    settings.DOCKER['IMAGE'] + ':' + settings.DOCKER['VERSION'],
                    volumes=None,
                    commands=''
                )
                # since we already in a thread, call block function instead of start another thread
                runner.run()

            # sleep random seconds between 5 ~ 30
            sleep(random_sleep)

