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
import time
sys.path.append("/home/video-analytics-serving/vaclient")
import vaclient

def on_connect(client, user_data, _unused_flags, return_code):
    if return_code == 0:
        args = user_data
        print("Connected to broker at {}:{}".format(args.broker_address, args.broker_port))
        print("Subscribing to topic {}".format(args.topic))
        client.subscribe(args.topic)
    else:
        print("Error {} connecting to broker".format(return_code))
        sys.exit(1)

def on_message(_unused_client, user_data, msg):
    result = json.loads(msg.payload)
    if not "frame_id" in result:
        return
    objects = result.get("objects", [])
    for obj in objects:
        label = obj["classification_layer_name:predictions_1/Softmax"]["label"]
        if label == user_data.defect:
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

def get_arguments():
    """Process command line options"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--uri',
                        action='store',
                        type=str,
                        default='file:///home/video-analytics-serving/data/textile.mp4',
                        help='Video URI')
    parser.add_argument('--topic',
                        action='store',
                        type=str,
                        default='vaserving',
                        help='Set MQTT topic')
    parser.add_argument('--broker-address',
                        action='store',
                        type=str,
                        default='localhost',
                        help='Set MQTT broker address')
    parser.add_argument('--broker-port',
                        action='store',
                        type=int,
                        default=1883,
                        help='Set MQTT broker port')
    parser.add_argument('--frame-store-template',
                        action='store',
                        type=str,
                        required=True,
                        help='Frame store file name template')
    parser.add_argument('--defect',
                        action='store',
                        type=str,
                        default='good',
                        choices=['color_flecks','good','hole','missing_pick','selvedge','stain'],
                        help='Defect of interest to display frames of')
    return parser.parse_args()

# Helper class to create vaclient arguments from command line arguments
class VAClientArgs():
    def __init__(self, args):
        self.pipeline = "object_classification/textile_defect"
        self.uri = args.uri
        self.destination = {
            "type" : "mqtt",
            "host": args.broker_address + ":" + str(args.broker_port),
            "topic" : args.topic,
        }
        self.parameters = {
            "file-location" : args.frame_store_template
        }
        self.verbose = False,
        self.show_request = False

if __name__ == "__main__":
    args = get_arguments()
    vaclient.start(VAClientArgs(args))
    client = mqtt.Client("Textile Defect Detector", userdata=args)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.broker_address, args.broker_port)
    client.loop_forever()
