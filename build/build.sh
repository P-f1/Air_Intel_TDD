#!/bin/bash

ProjectID=$1 
ServiceName=$2 
BuildFolder=$3 

echo "ProjectID = "$ProjectID
echo "ServiceName = "$ServiceName
echo "BuildFolder = "$BuildFolder
echo "EXT_HOME_DIR = " $EXT_HOME_DIR
echo "FRAMEWORK = " $FRAMEWORK

rm -rf ../artifacts/rtsf-at-checkout-reference-design
git clone https://github.com/intel-iot-devkit/rtsf-at-checkout-reference-design.git ../artifacts/rtsf-at-checkout-reference-design

cp -r ../artifacts/rtsf-at-checkout-reference-design/rtsf-at-checkout-cv-region-of-interest ./
cd ./rtsf-at-checkout-cv-region-of-interest
docker build -t cv-region-of-interest:dev ./
