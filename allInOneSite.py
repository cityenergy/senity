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

class allInOneSite:

    def __init__(self):
        self.sId = 0
        self.siteDevices = {}
        self.scheduler = BackgroundScheduler()
        self.client = mqtt.Client()
        self.senityLogger = logging.getLogger("senity_allInOneSite")

    # The callback for when the self.client receives a CONNACK response from the mqtt broker
    def __on_connect(self, client, userdata, flags, rc):

        self.senityLogger.info("Site " + str(self.sId) + " connected on mqtt broker with result code: " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect othen subscriptions will be renewed

        # Subscribe to initial configuration
        topic = con.TOPIC_SITE_DEVICES_CONF + "/" + str(self.sId)
        client.subscribe(topic)
        topic = con.TOPIC_SITE_CONF + "/" + str(self.sId)
        client.subscribe(topic)
        topic = con.TOPIC_SITE_DEVICE_STATUS + "/" + str(self.sId) + "/#"
        client.subscribe(topic)

    # The callback for when one of the topic messages is received from the mqtt broker
    def __on_message(self, client, userdata, msg):

        # Handle incoming messages
        try:
            msgPayload = ast.literal_eval(str(msg.payload))
        except Exception:
            self.senityLogger.error("Malformed messaged received in site: " + str(self.sId))

        # Site devices' configuration
        if msg.topic == con.TOPIC_SITE_DEVICES_CONF + "/" + str(self.sId):
            self.siteDevices = msgPayload
            self.senityLogger.info("Site " + str(self.sId) + " devices' configuration received.")

        # Site overall configuration
        elif msg.topic == con.TOPIC_SITE_CONF + "/" + str(self.sId):
            updateInterval = msgPayload
            self.scheduler.remove_job(con.MAIN_SITE_PERIODIC_JOB)
            self.scheduler.add_job(self.__runDevices, 'interval', seconds=updateInterval, id = con.MAIN_SITE_PERIODIC_JOB)
            self.senityLogger.info("Site " + str(self.sId) + " update interval to: " + str(updateInterval))

        # Update device status (on/off)
        elif (con.TOPIC_SITE_DEVICE_STATUS + "/" + str(self.sId)) in msg.topic:
            tmpString = (msg.topic).split("/")
            try:
                deviceId = int(tmpString[2])
            except Exception:
                self.senityLogger.error("Malformed messaged received in site: " + str(self.sId))
            self.siteDevices[deviceId]["status"] = msgPayload
            self.senityLogger.info("Site " + str(self.sId) + " device " + str(deviceId) + " status update received: " + str(self.siteDevices[int(deviceId)]["status"]))
            # publish new site devices configuration
            self.client.publish(con.TOPIC_SITE_DEVICES_CONF + "/" + str(self.sId), str(self.siteDevices), retain=True) 
        else:
            self.senityLogger.info(msg.topic)

    # Run the devices
    def __runDevices (self):

        for dId in self.siteDevices.keys():
            if self.siteDevices[dId]['status'] == 1 :
                self.client.publish(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(self.sId) + "/" + str(dId), str(self.siteDevices[dId]['avgConsumption']) )

    # Run "all in one" site main function
    def runSite (self, mqtt_broker_ip, mqtt_broker_port, siteId) :

        self.sId = siteId

        # Run Scheduler
        ch = logging.NullHandler()
        logging.getLogger('apscheduler.scheduler').addHandler(ch)
        logging.getLogger('apscheduler.scheduler').propagate = False
        self.scheduler.start()

        # Create, configure mqtt self.client and connect
        self.client.loop_start()
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message

        job = self.scheduler.add_job(self.__runDevices, 'interval', id = con.MAIN_SITE_PERIODIC_JOB)

        rc = self.client.connect(mqtt_broker_ip, mqtt_broker_port, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_forever()

def startSite(mqtt_broker_ip, mqtt_broker_port, siteId) :

    newSite = allInOneSite()
    newSite.runSite(mqtt_broker_ip, mqtt_broker_port, siteId)  
