#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SAMPLES_DIR=$(dirname $SCRIPT_DIR)
ROOT_DIR=$(dirname $SAMPLES_DIR)
TARGET_DIR=/home/video-analytics-serving/samples/textile_detect_classifier
IMAGE=video-analytics-serving-gstreamer
PIPELINE=object_classification/textile_defect
MEDIA=file:///home/video-analytics-serving/data/textile.mp4
BROKER_ADDR=localhost
BROKER_PORT=1883
TOPIC=vaserving
SPECIFIER="%08d"
DEFECT=

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --frame-store)
      if [ "$2" ]; then
        FRAME_STORE=$(readlink -f "$2")
        shift
      else
        echo "--frame-store expects a value"
        exit 1
      fi
      ;;
    --defect)
        if [ "$2" ]; then
            DEFECT="--defect $2"
            shift
        else
            echo "--defect expects a value"
            exit 1
        fi
        ;;
    *)
      ;;
  esac

  shift
done

if [ -z $FRAME_STORE ]; then
   echo Frame store path not specified
   exit 1
fi

FILE_LOCATION=$FRAME_STORE/$SPECIFIER.jpg
rm -f $FRAME_STORE/*.jpg
echo Frame store file location = $FILE_LOCATION
echo Starting mqtt client
ENTRYPOINT="python3"
ENTRYPOINT_ARGS="$TARGET_DIR/mqtt_client.py --broker-address $BROKER_ADDR --broker-port $BROKER_PORT --topic $TOPIC --frame-store-template $FILE_LOCATION $DEFECT"
VOLUME_MOUNT+="-v $HOME/.Xauthority:/home/video-analytics-serving/.Xauthority "
VOLUME_MOUNT+="-v $SCRIPT_DIR:$TARGET_DIR "
VOLUME_MOUNT+="-v $FRAME_STORE:$FRAME_STORE "
echo "$ROOT_DIR/docker/run.sh" $INTERACTIVE --name \"\" --network host --image $IMAGE $VOLUME_MOUNT -e DISPLAY --entrypoint $ENTRYPOINT --entrypoint-args "$ENTRYPOINT_ARGS"
