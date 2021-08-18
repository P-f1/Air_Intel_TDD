'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import argparse
import json
import paho.mqtt.client as mqtt
import cv2
import os.path
from os import path
import os
import time
sys.path.append("/home/video-analytics-serving/vaclient")
import vaclient

CAMERA0_SRC = os.environ['CAMERA0_SRC']
DEFECT = os.environ['DEFECT']
FRAME_STORE_TEMPLATE = os.environ['FRAME_STORE_TEMPLATE']
MQTT_BROKER_HOST = os.environ['MQTT_BROKER_HOST']
MQTT_BROKER_PORT = os.environ['MQTT_BROKER_PORT']
MQTT_BROKER_TOPIC = os.environ['MQTT_BROKER_TOPIC']

def on_connect(client, user_data, _unused_flags, return_code):
    if return_code == 0:
        args = user_data
        print("Connected to broker at {}:{}".format(args.broker_address, args.broker_port))
        print("Subscribing to topic {}".format(args.topic))
        client.subscribe(args.topic)
    else:
        print("Error {} connecting to broker".format(return_code))
        sys.exit(1)

def on_subscribe(client, userdata, message, qos):
    print("Subscribed to topic")

def on_message(_unused_client, user_data, msg):
    result = json.loads(msg.payload)
    if not "frame_id" in result:
        return
    objects = result.get("objects", [])
    for obj in objects:
        label = obj["classification_layer_name:predictions_1/Softmax"]["label"]
        if label == DEFECT:
            frame_id = result["frame_id"]
            print("FrameID {}: defect = {}".format(frame_id, label))
            args = user_data
            frame_path = args.frame_store_template % frame_id
            print("Frame path: {}".format(frame_path))
            if wait_for_frame(frame_path):
                frame = cv2.imread(frame_path)
                image = cv2.resize(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)))
#                cv2.imshow(label, image)
#                cv2.waitKey(0)
#                cv2.destroyAllWindows()
            break

# Due to pipeline timing frame save may not have completed by the time its metadata has been published
def wait_for_frame(frame_path):
    retry_count = 0
    while not path.exists(frame_path):
        if retry_count > 10:
            print("Error: File not found")
            return False
        time.sleep(0.1)
        retry_count += 1
    return True

# Helper class to create vaclient arguments from command line arguments
class VAClientArgs():
    def __init__(self, args):
        self.pipeline = "object_classification/textile_defect"
        self.uri = CAMERA0_SRC
        self.destination = {
            "type" : "mqtt",
            "host": MQTT_BROKER_HOST + ":" + str(MQTT_BROKER_PORT),
            "topic" : MQTT_BROKER_TOPIC,
        }
        self.parameters = {
            "file-location" : FRAME_STORE_TEMPLATE
        }
        self.verbose = False,
        self.show_request = False

if __name__ == "__main__":
    
    vaclient.start(VAClientArgs(args))
    client = mqtt.Client("Textile Defect Detector", userdata=args)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    client.loop_forever()
