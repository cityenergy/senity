# This script emulates the operation of a single site including the gateway,
# the local demand response system (ldrms) - if any - and the associated devices.
import constants as con

import sys
import ast
import paho.mqtt.client as mqtt
import logging
import multiprocessing

## mqtt broker settings
#if len(sys.argv) < 2 :
#    print "More inpurt paramters are required"
#    sys.exit(0) 
#else:
#    mqtt_broker_ip = sys.argv[1] 
#    mqtt_broker_port = 1883

# The callback for when the client receives a CONNACK response from the mqtt broker
def on_connect(client, userdata, flags, rc):

    logging.info("Site " + str(sId) + " connected on mqtt broker with result code: " + str(rc))
   
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect othen subscriptions will be renewed
    
    # Subscribe to initial configuration
    topic = con.TOPIC_SITE_CONF + "/" + str(sId)
    client.subscribe(topic)

# The callback for when one of the topic messages is received from the mqtt broker
def on_message(client, userdata, msg):
    
    print msg.topic+ " " + str(msg.payload)

    sId = userdata

    if msg.topic == con.TOPIC_SITE_CONF + "/" + str(sId):
        logging.info("Site configuration received from site " + str(sId))
        try:
            deviceProfiles = ast.literal_eval(str(msg.payload))
        except Exception:
            logging.error("Malformed messaged received in site: " + str(sId))

        createDevices(deviceProfiles)
        
# Run "all in one" site main function
def runSite (mqtt_broker_ip, mqtt_broker_port, siteId) :

    global sId
    sId = siteId

    # Create, configure mqtt client and connect 
    client = mqtt.Client(userdata=sId)
    client.loop_start()
    client.on_connect = on_connect
    client.on_message = on_message

    rc = client.connect(mqtt_broker_ip, mqtt_broker_port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

# Create all device processes
def createDevices (deviceProfiles) :

    deviceProcs = []
    deviceId = 0
    for device in deviceProfiles:
        sp = multiprocessing.Process(target=runDevice, args=(device, deviceId))
        deviceProcs.append(sp)
        sp.start()
        deviceId = deviceId + 1

# Run a device
def runDevice (profile, deviceId):
    
    logging.info("Site " + str(sId) + " creates device " + str(deviceId) + " with profile " + str(profile)) 
