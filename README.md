# HYPR.AI

A cloud-based deep learning and hyperparameter optimization platform.

This package provides a solution of automated training system for deep learning. It contains a restful service, dockerized training worker and an example WebUI build upon restful service.


### Features:

-   Use predefined JSON file to define deep learning network architetures
-   Support modular models to reduce the complexity of building similar models
-   Pretrained model can be loaded into extended network architectures
-   Training instances (dockerized container) can be deployed to anywhere
-   In a "hypr task", the user specifies hyperparameters to explore, creating multiple trainings


![screen](media/main_screenshot.png)


## Requirements  

-   Python 3
-   Docker 17.03 or above
-   AWS Access key with fullaccess of S3 and DynamoDB
-   Nvidia GPU (training instance)


## How to deploy

Two kinds of services need to be deployed:

A. Restful service (ONLY need one)
B. Training instances (Not limited, the more the better)


### Prerequisite

#### Docker

Both restful service and training instance require Docker:

Here is the tutorial for installing Docker on Ubuntu: https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

#### GPU ready(training instance only)

The training instance require:Nvidia driver, CUDA8.0 and nvidia-docker

Example bash script for GPU ready(Ubuntu):

``` bash
# install nvidia driver and cuda
sudo add-apt-repository ppa:graphics-drivers/ppa -y
sudo apt update
sudo apt install nvidia-375 -y
wget https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64-deb
sudo dpkg -i cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64-deb
sudo apt-get update
sudo apt-get install cuda -y
# Install nvidia-docker
wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb
sudo dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb
# Test nvidia-docker
sudo nvidia-docker run --rm nvidia/cuda nvidia-smi
```

### A. Restful service
It's highly recommend to run restful service on AWS which will have short latency on accessing DynamoDB and S3, but it still can be deployed to your local machine (make sure that machine can be accessed through internet otherwise the logs come from training instance will be lost).

The recommended EC2 instance is at least: `t2.xlarge` or `m4.xlarge`

1). Clone `https://github.com/rreece/hypr-ai.git` to where you want to deploy restful service

2). Change the `Monitor Service` and `Docker Image of Worker` in `hypr-ai/settings.py`

```Python
DOCKER = {
    'IMAGE': 'insight/tworker',
    'VERSION': 'latest'
}
MONITOR = {
    'HOST': 'http://[YOUR IP or DOMAIN where running restful service]',
    'PATH': '/monitor'
}
```

3). Build the `service` docker image

``` docker
    docker build -t insight/kservice -f Dockerfile.service .
``` 

4). Start the service

```bash
    ./start_restful_docker_service.sh
```

### B. Training instance
The training instance can be depolyed to anywhere as long as the machine contains nvidia GPU and running Linux. It's NOT necessary to keep the training instance running all the time. You can add tasks to system first, then start one or more training instances to run these tasks.

1). Clone `https://github.com/rreece/hypr-ai.git` to where you want to deploy training instance

2). Build the `worker` docker image

``` docker
    docker build -t insight/tworker -f Dockerfile.worker .
```

3). Export Environment variable in training instance(temporary)

Add following environment variables with your AWS keys to ~/.bashrc

``` bash
export AWS_ACCESS_KEY_ID={ACCESS_KEY}
export AWS_SECRET_ACCESS_KEY={SECRET_KEY}
export AWS_DEFAULT_REGION={REGION}
```

4). Start `Agent` service on training instance(each time when you start the training instance)

``` bash
nvidia-docker run --rm -it --name insight --hostname {YOUR INSTANCE NAME} -v /var/run/docker.sock:/var/run/docker.sock -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} insight/tworker
```

### C. Final step: AWS credentials

Access the system through:

    http://[YOUR IP or DOMAIN where running restful service]

Set the AWS credentials by clicking the `setting` on the left:
![aws](media/aws_setting.png)

AWS regions:

| Region name  | Region |
| ------------- | ------------- |
| US East (Ohio)  | us-east-2  |
| US East (N.Virginia)  | us-east-1  |
| US West (N.California) |	us-west-1 |
| US West (Oregon) | us-west-2 |


## Structure of package

    Dockerfile.service      Docker file for Restful service
    Dockerfile.worker       Docker file for Training instance
    cli.sh                  bash script redirect to cli.py
    - package               Python package main folder
        - insight
            - __init__.py
            - agent.py
            - applications
                - AgentService.py       Agent service entrance
                - RESTservice.py        Restfull service entrace
                - cli.py                A command-line based client
                - settings.py           general settings
                - worker.py             Worker entity run inside docker
            - builder.py                Model builder
            - optimizer.py              Generator for hyperparameter optimization
            - storage.py                Manipulate AWS DynamoDB and S3
            - web                       All Web related code
                REST_server.py          Back-end, Restful service
                - static                Front-end
                    css
                    fonts
                    images
                    index.html          Main html
                    js
        setup.py
        - test
            service_test.py
            unit_test.py
    run_agentservice.sh               Shortcut to start agent service
    run_restservice.sh                Shortcut to start restful service
    run_worker.sh                     Docker.worker entry point
    settings.py                       Setting file refer by docker container
    start_restful_docker_service.sh   bash script of starting docker container to run restful service
    start_worker_docker_service.sh    bash script of starting docker container to run worker service


## Authors

-   Ryan Reece  <ryan.reece@cern.ch>
-   Jiaming "Jimmy" Hu  <https://github.com/JMHOO/planet-insight>


