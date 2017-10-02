#!/bin/sh
PORT=""
while getopts ":p:" opt; do
  case $opt in
	p)
	PORT=$OPTARG
	;;
  esac
done

python3 ./package/insight/web/REST_server.py --port=${PORT}