# This script emulates the operation of a single site including the gateway,
# the local demand response system (ldrms) - if any - and the associated devices.

import sys
import paho.mqtt.client as mqtt

## mqtt broker settings
#if len(sys.argv) < 2 :
#    print "More inpurt paramters are required"
#    sys.exit(0) 
#else:
#    mqtt_broker_ip = sys.argv[1] 
#    mqtt_broker_port = 1883

# topic for initial configuration parameters
topic_initial_conf = "initial_conf"

# The callback for when the client receives a CONNACK response from the mqtt broker
def on_connect(client, userdata, flags, rc):

    print "Connected on mqtt broker with result code: " + str(rc)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed
    client.subscribe(topic_initial_conf)

# The callback for when one of the topic messages is received from the mqtt broker
def on_message(client, userdata, msg):
    print msg.topic+ " " + str(msg.payload)

# Run "all in one" site main function
def runSite (mqtt_broker_ip, mqtt_broker_port) :

    # Create, configure mqtt client and connect 
    client = mqtt.Client()
    client.loop_start()
    client.on_connect = on_connect
    client.on_message = on_message

    rc = client.connect(mqtt_broker_ip, mqtt_broker_port, 60)
    client.subscribe(topic_initial_conf)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
