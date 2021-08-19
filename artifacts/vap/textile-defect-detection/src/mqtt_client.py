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
import requests 

EDGEX_DEVICE_NAME = os.environ['EDGEX_DEVICE_NAME']
EDGEX_TDD_EVENT = os.environ['EDGEX_TDD_EVENT']
CAMERA0_SRC = os.environ['CAMERA0_SRC']
DEFECT = os.environ['DEFECT']
FRAME_STORE_TEMPLATE = os.environ['FRAME_STORE_TEMPLATE']
MQTT_BROKER_HOST = os.environ['MQTT_BROKER_HOST']
MQTT_BROKER_PORT = os.environ['MQTT_BROKER_PORT']
MQTT_BROKER_TOPIC = os.environ['MQTT_BROKER_TOPIC']
MQTT_OUTBOUND_TOPIC_NAME = os.environ['MQTT_OUTBOUND_TOPIC_NAME']
MQTT_KEEPALIVE = 12*60*60

def on_connect(client, user_data, _unused_flags, return_code):
    print("On connect!")
    if return_code == 0:
        print("Connected to broker at {}:{}".format(MQTT_BROKER_HOST, MQTT_BROKER_PORT))
        print("Subscribing to topic {}".format(MQTT_BROKER_TOPIC))
        client.subscribe(MQTT_BROKER_TOPIC)
    else:
        print("Error {} connecting to broker".format(return_code))
        sys.exit(1)

def on_subscribe(client, userdata, message, qos):
    print("Subscribed to topic!")

def on_message(out_bound_client, user_data, msg):
    print("On Message!")
    result = json.loads(msg.payload)
#    print(result)
    if not "frame_id" in result:
        return
    objects = result.get("objects", [])
    for obj in objects:
        label = obj["classification_layer_name:predictions_1/Softmax"]["label"]
        target_defect = obj["tags"]["target_defect"]
        if label == target_defect or "*" == target_defect:
            frame_id = result["frame_id"]
            frame_path = FRAME_STORE_TEMPLATE % frame_id
            prediction = {}
            prediction["source"] = obj['source']
            prediction["target_defect"] = target_defect
            prediction["label"] = label
            prediction["frame_path"] = frame_path
            prediction["timestamp"] = EDGEX_ENTER_EVENT
            out_bound_client.publish(MQTT_OUTBOUND_TOPIC_NAME, wrap_edgex_event(EDGEX_DEVICE_NAME, EDGEX_TDD_EVENT, json.dumps(prediction)))
    
def wrap_edgex_event(device_name, cmd_name, data):
    edgexMQTTWrapper = {}
    edgexMQTTWrapper["name"] = device_name
    edgexMQTTWrapper["cmd"] = cmd_name
    edgexMQTTWrapper[cmd_name] = data
    print(edgexMQTTWrapper)
    return json.dumps(edgexMQTTWrapper)

def send_request_to_vas():
    data = {}
    data['source'] = camConfig['source']
    data['destination'] =  camConfig['destination']   
    data['tags'] =  camConfig['tags']  
    data['parameters'] = camConfig['parameters']       
    jsonData = json.dumps(data)            
    endpoint = camConfig['camEndpoint']  
    print(jsonData)
    headers = {'Content-type': 'application/json'}
    r = requests.post(url = endpoint, data = jsonData, headers = headers) 
    if r.status_code == 200:
        print("Created new pipeline with id: %s"%r.text)
    else:
        print("Error creating pipeline: %s"%r)


if __name__ == "__main__":

    print("EDGEX_DEVICE_NAME        : {}".format(EDGEX_DEVICE_NAME))
    print("EDGEX_TDD_EVENT          : {}".format(EDGEX_TDD_EVENT))
    print("CAMERA0_SRC              : {}".format(CAMERA0_SRC))
    print("DEFECT                   : {}".format( DEFECT))
    print("FRAME_STORE_TEMPLATE     : {}".format(FRAME_STORE_TEMPLATE))
    print("MQTT_BROKER_HOST         : {}".format(MQTT_BROKER_HOST))
    print("MQTT_BROKER_PORT         : {}".format(MQTT_BROKER_PORT))
    print("MQTT_BROKER_TOPIC        : {}".format(MQTT_BROKER_TOPIC))
    print("MQTT_OUTBOUND_TOPIC_NAME : {}".format(MQTT_OUTBOUND_TOPIC_NAME))
    print("MQTT_KEEPALIVE           : {}".format(12*60*60))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    
    try:
        client.connect(MQTT_BROKER_HOST, int(MQTT_BROKER_PORT), MQTT_KEEPALIVE)
        client.loop_forever()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("WARNING: Textile defect detection service could not connect to mqtt broker, no messages will be produced")

