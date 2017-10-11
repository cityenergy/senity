# The overall emulation Manager, which is responsible for starting and configuring the various entities
import constants as con

import sys
import paho.mqtt.client as mqtt
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
import re

class console :

    def __init__(self, mqtt_broker_ip, mqtt_broker_port, console_cmd_waiting):
        self.commBusClient = mqtt.Client()    
        self.foundSites = []
        self.foundSiteDevices = []
        self.deviceConsumptionData = []
        self.searchForSiteId = -1
        self.siteDeviceId = -1
        self.mqtt_broker_ip = mqtt_broker_ip
        self.mqtt_broker_port = mqtt_broker_port
        self.console_cmd_waiting = console_cmd_waiting

    # Handle output during console waiting for command to return
    def __consoleWaitOutput(self):
        for i in range(self.console_cmd_waiting):
            print ".",
            sys.stdout.flush()
            time.sleep(0.2)

    # The callback for when the client receives a CONNACK response from the mqtt broker
    def __on_connect(self, client, userdata, flags, rc):

        pass
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect othen subscriptions will be renewed

    # The callback for when one of the topic messages is received from the mqtt broker
    def __on_message(self, client, userdata, msg):
        if (con.TOPIC_SITE_CONF + "/") in msg.topic:
            tmpString = (msg.topic).split("/")
            try:
                siteId = int(tmpString[1])
                self.foundSites.append(siteId)
            except Exception:
                 print("Malformed messaged received by console")
        elif(con.TOPIC_SITE_DEVICES_CONF + "/" + str(self.searchForSiteId)) in msg.topic:
            self.foundSiteDevices.append(str(msg.payload))
        elif(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(self.siteDeviceId)) in msg.topic:
            self.deviceConsumptionData.append(str(msg.payload))

    # Connect to the communication bus
    def __connectToCommBus(self, userdata="") :

        # Create, configure mqtt client and connect
        self.commBusClient.loop_start()
        self.commBusClient.on_connect = self.__on_connect
        self.commBusClient.on_message = self.__on_message

        try:
            rc = self.commBusClient.connect(self.mqtt_broker_ip, self.mqtt_broker_port, 60)
        except Exception:
            print("Error while conencting to communication bus. Check whether the respective service is running.")
            sys.exit(0)

    # Start console         
    def start(self) :
        # Connect to communication bus
        # Note: Perhaps is seems strange at first that both the emulationManager and the console functionallity are connected
        # seperately to the communication bus. This is more of a desing/architecturel approach so as to seperate operations that
        # the emulationManager has to pass to the communication bus to setup the emulation and the ones that other entities pass so
        # as to retrieve and set parameters
        self.__connectToCommBus()    

        # Available commands
        availableCommands = ["sites", "site", "device_on", "device_off", "device_consumption", "help", "exit"]
        Completer = WordCompleter(availableCommands)

        # Console loop
        memHistory = InMemoryHistory()
        while True:
            # Handle the case where the commands has multiple arguments
            cmdFull = prompt(unicode(con.CONSOLE_PROMPT), history=memHistory, completer=Completer)
            cmdSplit = cmdFull.split()
            if not cmdFull == "":
                cmd = cmdSplit[0]
            else:
                continue

            if cmd in availableCommands:
                if cmd == "exit" :
                    print("'There is a kind of senity in love which is almost a paradise'")
                    break
                elif cmd == "help" :
                    print("Available commands: " + str(availableCommands))
                elif cmd == "sites":
                    self.foundSites = []
                    self.commBusClient.subscribe(con.TOPIC_SITE_CONF + "/#")
                    self.__consoleWaitOutput()
                    self.commBusClient.unsubscribe(con.TOPIC_SITE_CONF + "/#")
                    print("\nSites found: " + str(self.foundSites))
                elif cmd == "site":
                    if(len(cmdSplit) == 2 and re.match('(\d+)', cmdSplit[1])):
                        self.searchForSiteId = cmdSplit[1]
                        self.foundSiteDevices = []
                        self.commBusClient.subscribe(con.TOPIC_SITE_DEVICES_CONF + "/" + self.searchForSiteId)
                        self.__consoleWaitOutput()
                        self.commBusClient.unsubscribe(con.TOPIC_SITE_DEVICES_CONF + "/" + self.searchForSiteId)
                        print("\nDevices found in Site " + str(self.searchForSiteId) + " :\n" + str(self.foundSiteDevices))
                        self.searchForSiteId = -1
                    else:
                        print("Wrong syntax: site <site id>")
                elif cmd == "device_on":
                    if(len(cmdSplit) == 2 and re.match('(\d+)/(\d+)', cmdSplit[1])):
                        self.siteDeviceId = cmdSplit[1]
                        self.commBusClient.publish(con.TOPIC_SITE_DEVICE_STATUS + "/" + str(self.siteDeviceId), str(1))
                    else:
                        print("Wrong syntax: device_on <site id>/<device id>")
                elif cmd == "device_off":
                    if(len(cmdSplit) == 2 and re.match('(\d+)/(\d+)', cmdSplit[1])):
                        self.siteDeviceId = cmdSplit[1]
                        self.commBusClient.publish(con.TOPIC_SITE_DEVICE_STATUS + "/" + str(self.siteDeviceId), str(0))
                    else:
                        print("Wrong syntax: device_on <site id>/<device id>")
                elif cmd == "device_consumption":
                    if(len(cmdSplit) == 2 and re.match('(\d+)/(\d+)', cmdSplit[1])):
                        self.siteDeviceId = cmdSplit[1]
                        self.deviceConsumptionData = []
                        self.commBusClient.subscribe(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(self.siteDeviceId))
                        self.__consoleWaitOutput()
                        self.commBusClient.unsubscribe(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(self.siteDeviceId))
                        print("\nDevice " + str(self.siteDeviceId) + " consumption :\n" + str(self.deviceConsumptionData))
                        self.siteDeviceId = -1
                    else:
                        print("Wrong syntax: device_consumption <site id>/<device id>")
            else:
                print("Command not found")     


