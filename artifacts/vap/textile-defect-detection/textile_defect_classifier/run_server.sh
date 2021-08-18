#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$SCRIPT_DIR/../..")

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
    *)
      ;;
  esac

  shift
done

if [ -z $FRAME_STORE ]; then
   echo Frame store path not specified
   exit 1
fi

mkdir -p $FRAME_STORE
chmod -R a+rwx $FRAME_STORE
rm -f $FRAME_STORE/*
VOLUME_MOUNT+="-v $SCRIPT_DIR/extensions/add_frame_id.py:/home/video-analytics-serving/extensions/add_frame_id.py "
VOLUME_MOUNT+="-v $FRAME_STORE:$FRAME_STORE "
VOLUME_MOUNT+="-v $SCRIPT_DIR/data:/home/video-analytics-serving/data "
"$ROOT_DIR/docker/run.sh" --network host --pipelines $SCRIPT_DIR/pipelines --models $SCRIPT_DIR/models $VOLUME_MOUNT "$@"
