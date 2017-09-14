# This script emulates the operation of a single site including the gateway,
# the local demand response system (ldrms) - if any - and the associated devices.
import constants as con

import sys
import ast
import paho.mqtt.client as mqtt
import logging
import multiprocessing
import random
from apscheduler.schedulers.background import BackgroundScheduler

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
    topic = con.TOPIC_SITE_DEVICES_CONF + "/" + str(sId)
    client.subscribe(topic)
    topic = con.TOPIC_SITE_CONF + "/" + str(sId)
    client.subscribe(topic)

# The callback for when one of the topic messages is received from the mqtt broker
def on_message(client, userdata, msg):
    
    scheduler = userdata

    # Handle incoming messages
    if msg.topic == con.TOPIC_SITE_DEVICES_CONF + "/" + str(sId):
        logging.info("Site " + str(sId) + " devices' configuration received from site.")
        try:
            deviceProfiles = ast.literal_eval(str(msg.payload))
        except Exception:
            logging.error("Malformed messaged received in site: " + str(sId))

        processDeviceProfiles(deviceProfiles)

    elif msg.topic == con.TOPIC_SITE_CONF + "/" + str(sId):
        logging.info("Site " + str(sId) + " configuration received from site.")
        try:
            updateInterval = ast.literal_eval(str(msg.payload))
        except Exception:
            logging.error("Malformed messaged received in site: " + str(sId))

        scheduler.remove_job(con.MAIN_SITE_PERIODIC_JOB) 
        scheduler.add_job(runDevices, 'interval', seconds=updateInterval, id = con.MAIN_SITE_PERIODIC_JOB)
        logging.info("Site " + str(sId) + " update updateInterval to: " + str(updateInterval))
    else:
        lala = ast.literal_eval(str(msg.payload))
     
        
# Run "all in one" site main function
def runSite (mqtt_broker_ip, mqtt_broker_port, siteId) :

    global sId, siteDevices, client
    sId = siteId
    siteDevices = {}

    # Run Scheduler
    logging.getLogger('apscheduler').propagate = False
    scheduler = BackgroundScheduler()
    scheduler.start()
    job = scheduler.add_job(runDevices, 'interval', id = con.MAIN_SITE_PERIODIC_JOB)

    # Create, configure mqtt client and connect 
    client = mqtt.Client(userdata=scheduler)
    client.loop_start()
    client.on_connect = on_connect
    client.on_message = on_message

    rc = client.connect(mqtt_broker_ip, mqtt_broker_port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

# Process device profiles
def processDeviceProfiles (deviceProfiles):

    deviceId = 0

    for profile in deviceProfiles:
        siteDevices[deviceId] = {'profile': profile, 'status': 1}
        deviceId = deviceId + 1

# Run the devices
def runDevices ():
  
    for dId in siteDevices.keys():
        client.publish(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(sId) + "/" + str(dId), str(siteDevices[dId]['profile']['avgConsumption']) )
