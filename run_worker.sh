#!/bin/sh
INSTANCE_NAME=""
MODEL_NAME=""
WEIGHTS_FILE=""
DATASET_FILE=""
Train=false
# processing command options
while getopts ":i:m:w:d" opt; do
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
	\?)
	echo "Invalid option: -$OPTARG"
	exit 1
	;;
  esac
done

python3 ./package/insight/application/worker.py --instance=${INSTANCE_NAME} --model=${MODEL_NAME} --weights=${WEIGHTS_FILE} --dataset=${DATASET_FILE}
