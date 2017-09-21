#!/bin/sh
INSTANCE_NAME=""
MODEL_NAME=""
WEIGHTS_FILE=""
DATASET_FILE=""
MONITOR_SERVICE=""
# processing command options
while getopts ":i:m:w:d:s" opt; do
  case $opt in
	i)
	INSTANCE_NAME=$OPTARG
	;;
    m)
	MODEL_NAME=$OPTARG
	;;
	w)
	WEIGHTS_FILE=$OPTARG
    ;;
    d)
	DATASET_FILE=$OPTARG
	;;
    s)
    MONITOR_SERVICE=$OPTARG
    ;;
	\?)
	echo "Invalid option: -$OPTARG"
	exit 1
	;;
  esac
done

python3 ./package/insight/applications/worker.py --instance=${INSTANCE_NAME} --model=${MODEL_NAME} --weights=${WEIGHTS_FILE} --dataset=${DATASET_FILE} --service=${MONITOR_SERVICE}
