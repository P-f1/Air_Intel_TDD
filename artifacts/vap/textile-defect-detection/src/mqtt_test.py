'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import argparse
import json
import paho.mqtt.client as mqtt
import os.path
from os import path
import os
import time

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = "1883"
MQTT_BROKER_TOPIC = "EdgexGatewayData"
MQTT_OUTBOUND_TOPIC_NAME = "AIRData"
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
    out_bound_client.publish(MQTT_OUTBOUND_TOPIC_NAME, "My hello!")

if __name__ == "__main__":

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
        print("Unexpected error:", sys.exc_info())
        print("WARNING: Textile defect detection service could not connect to mqtt broker, no messages will be produced")

