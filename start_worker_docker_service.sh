#!/bin/bash

if [[ "$(docker images -q insight/tworker 2> /dev/null)" == "" ]]; then
    docker build -t insight/tworker -f Dockerfile.worker .
fi

nvidia-docker run --rm -it --name insight --hostname $USER -v /var/run/docker.sock:/var/run/docker.sock -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} insight/tworker

