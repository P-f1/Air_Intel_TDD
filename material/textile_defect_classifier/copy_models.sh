#!/bin/bash -e
#
# Copyright (C) 2021 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
if [ $# -ne 1 ]; then
    echo "Must specify path to reference implementation download"
    exit 1
fi

if [ ! -d $1/models ]; then
    echo "Reference implementation directory must include models folder"
    exit 1
fi

REF_SRC_DIR=$1
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SAMPLES_DIR=$(dirname $SCRIPT_DIR)
echo "Reference implementation folder: $REF_SRC_DIR"
echo "VA Serving sample folder: $SCRIPT_DIR"
MODELS_DIR=$SCRIPT_DIR/models/object_classification/textile-defect
mkdir -p $MODELS_DIR/FP16
mkdir -p $MODELS_DIR/FP32
mkdir -p $SCRIPT_DIR/data
cp $REF_SRC_DIR/models/* $MODELS_DIR/FP16
cp $REF_SRC_DIR/models/* $MODELS_DIR/FP32
cp $REF_SRC_DIR/data/*.mp4 $SCRIPT_DIR/data
