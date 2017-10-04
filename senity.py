# The overall emulation Manager, which is responsible for starting and configuring the various entities
import constants as con
import emulationManager

import sys
import paho.mqtt.client as mqtt
import argparse
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
import re

# Parse command line arguments
def parseArguments ():

    parser = argparse.ArgumentParser("senity")
    parser.add_argument('-c', nargs=1, help="The configuration file")
    parser.add_argument('-s', nargs=1, help="The emulation scenario file")
    args = parser.parse_args()

    try:
        return args.c[0], args.s[0]
    except Exception:
        parser.print_help()
        sys.exit(0)

# Handle output during console waiting for command to return
def consoleWaitOutput(console_cmd_waiting):
    for i in range(console_cmd_waiting):
        print ".",
        sys.stdout.flush()
        time.sleep(0.2)

# The callback for when the client receives a CONNACK response from the mqtt broker
def on_connect(client, userdata, flags, rc):

    pass
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect othen subscriptions will be renewed

# The callback for when one of the topic messages is received from the mqtt broker
def on_message(client, userdata, msg):
    if (con.TOPIC_SITE_CONF + "/") in msg.topic:
        tmpString = (msg.topic).split("/")
        try:
            siteId = int(tmpString[1])
            foundSites.append(siteId)
        except Exception:
             print("Malformed messaged received by Senity emulation manager")
    elif(con.TOPIC_SITE_DEVICES_CONF + "/" + str(searchForSiteId)) in msg.topic:
        foundSiteDevices.append(str(msg.payload))
    elif(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(siteDeviceId)) in msg.topic:
        deviceConsumptionData.append(str(msg.payload))


global foundSites
global searchForSiteId
global siteDeviceId
global foundSiteDevices
global deviceConsumptionData
searchForSiteId = -1
siteDeviceId = -1

# Read input parameters
(conf_file, scenario_file) = parseArguments()

# Start emulation Manager
emulManager = emulationManager.emulationManager()
emulManager.start(conf_file, scenario_file)

# Connect to communication bus
# Note: Perhaps is seems strange at first that both the emulationManager and the console functionallity are connected
# seperately to the communication bus. This is more of a desing/architecturel approach so as to seperate operations that
# the emulationManager has to pass to the communication bus to setup the emulation and the ones that other entities pass so
# as to retrieve and set parameters 
client = mqtt.Client()
client.loop_start()
client.on_connect = on_connect
client.on_message = on_message
(mqtt_broker_ip, mqtt_broker_port, console_cmd_waiting) = emulManager.getConfParams()
client.connect(mqtt_broker_ip, mqtt_broker_port, 60)

# Start console

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
            foundSites = []
            client.subscribe(con.TOPIC_SITE_CONF + "/#")
            consoleWaitOutput(console_cmd_waiting)
            client.unsubscribe(con.TOPIC_SITE_CONF + "/#")
            print("\nSites found: " + str(foundSites))
        elif cmd == "site":
            if(len(cmdSplit) == 2 and re.match('(\d+)', cmdSplit[1])):
                searchForSiteId = cmdSplit[1]
                foundSiteDevices = []
                client.subscribe(con.TOPIC_SITE_DEVICES_CONF + "/" + searchForSiteId)
                consoleWaitOutput(console_cmd_waiting)
                client.unsubscribe(con.TOPIC_SITE_DEVICES_CONF + "/" + searchForSiteId)
                print("\nDevices found in Site " + str(searchForSiteId) + " :\n" + str(foundSiteDevices))
                searchForSiteId = -1
            else:
                print("Wrong syntax: site <site id>")
        elif cmd == "device_on":
            if(len(cmdSplit) == 2 and re.match('(\d+)/(\d+)', cmdSplit[1])):
                siteDeviceId = cmdSplit[1]
                client.publish(con.TOPIC_SITE_DEVICE_STATUS + "/" + str(siteDeviceId), str(1))
            else:
                print("Wrong syntax: device_on <site id>/<device id>")
        elif cmd == "device_off":
            if(len(cmdSplit) == 2 and re.match('(\d+)/(\d+)', cmdSplit[1])):
                siteDeviceId = cmdSplit[1]
                client.publish(con.TOPIC_SITE_DEVICE_STATUS + "/" + str(siteDeviceId), str(0))
            else:
                print("Wrong syntax: device_on <site id>/<device id>")
        elif cmd == "device_consumption":
            if(len(cmdSplit) == 2 and re.match('(\d+)/(\d+)', cmdSplit[1])):
                siteDeviceId = cmdSplit[1]
                deviceConsumptionData = []
                client.subscribe(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(siteDeviceId))
                consoleWaitOutput(console_cmd_waiting)
                client.unsubscribe(con.TOPIC_SITE_DEVICE_CONSUMPTION + "/" + str(siteDeviceId))
                print("\nDevice " + str(siteDeviceId) + " consumption :\n" + str(deviceConsumptionData))
                siteDeviceId = -1
            else:
                print("Wrong syntax: device_consumption <site id>/<device id>")
    else:
        print("Command not found")

# Close emulation manager
emulManager.closeSenity()
