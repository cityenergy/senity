# The overall emulation Manager, which is responsible for starting and configuring the various entities
import getScenarioConf
import getDeviceProfile
import getSiteProfile
import allInOneSite
import constants as con

import sys
import paho.mqtt.client as mqtt
import multiprocessing
import ConfigParser
import argparse
import logging
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter

# Init logging functionallity
def initLogging (log_file):
    if not log_file:
        logging.propagate = False
    else: 
        global senityLogger
        senityLogger = logging.getLogger("senity_emulationManager")
        logging.basicConfig(format='%(asctime)s : %(message)s', filename=log_file,level=logging.DEBUG)

# Parse command line arguments
def parseArguments ():

    parser = argparse.ArgumentParser("senity")
    parser.add_argument('-c', nargs=1, help="The configuration file")
    parser.add_argument('-s', nargs=1, help="The emulation scenario file")
    args = parser.parse_args()

    return args.c[0], args.s[0]

# Read configuration parameters
def readConfiguration (conf_file):

    config = ConfigParser.ConfigParser()
    try:
        config.read(conf_file)
    except Exception:
        print("Could not read configuration file: " + conf_file)
        sys.exit(0)

    devices_folder = config.get('General', 'devices_folder')
    sites_folder = config.get('General', 'sites_folder')
    mqtt_broker_ip =  config.get('General', 'mqtt_broker_ip')
    mqtt_broker_port = config.get('General', 'mqtt_broker_port')
    log_file = config.get('General', 'log_file')
    
    return devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, log_file

# Check that profiles and configuration data are valid and return ready format configuration to send to each site
def validateFormatScenario (scenarioConf, allSites, allDevices) : 

    sitesConf = {}
    for site in scenarioConf:
        dId = 0
        if not allSites.has_key(site):
            senityLogger.error("Site name '" + str(site) +"' not found, check configurations")
            sys.exit(0)
        sitesConf[site] = {}
        for device in allSites[site]:
            if not allDevices.has_key(device):
                senityLogger.error("Device name '" + device +"' not found, check configurations")
                sys.exit(0)
            sitesConf[site][dId]=allDevices[device]
            dId = dId + 1

    return sitesConf

# The callback for when the client receives a CONNACK response from the mqtt broker
def on_connect(client, userdata, flags, rc):

     senityLogger.info("Emulation Manager connected on mqtt broker with result code: " + str(rc))

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
             senityLogger.error("Malformed messaged received by Senity emulation manager")

    #print msg.topic+ " " + str(msg.payload)


# Connect to the communication bus
def connectToCommBus(mqtt_broker_ip, mqtt_broker_port, userdata="") :

    # Create, configure mqtt client and connect
    client = mqtt.Client()
    client.loop_start()
    client.on_connect = on_connect
    client.on_message = on_message

    rc = client.connect(mqtt_broker_ip, mqtt_broker_port, 60)

    return client

# Closing and exiting senity
def closeSenity(siteProcs):
    for sp in siteProcs:
        sp.terminate()


global foundSites 

# Read input parameters
(conf_file, scenario_file) = parseArguments()
#print conf_file, scenario_file

# Read configuration
(devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, log_file) = readConfiguration(conf_file)
#print devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port

# Init logging
initLogging(log_file)

# read devices and sites profiles and emulation scenarion configuration
try:
    allDevices = getDeviceProfile.getAllDeviceProfiles(devices_folder)
    allSites = getSiteProfile.getAllSiteProfiles(sites_folder)
except Exception:
    senityLogger.error("Device and/or site profiles could not be loaded.")
    sys.exit(0)

try:
    (updateInterval, scenarioConf) = getScenarioConf.getScenarioConf(scenario_file)
except Exception:
    senityLogger.error("Scenario configuration could not be loaded.")
    sys.exit(0)

# Connect to comm bus
commBusClient = connectToCommBus(mqtt_broker_ip, mqtt_broker_port)

# validate data and return sites configuration
sitesConf = validateFormatScenario(scenarioConf, allSites, allDevices)

# Create emulated "all in one" sites
siteProcs = []
siteId = 0
for site in sitesConf.keys():
    sp = multiprocessing.Process(target=allInOneSite.startSite, args=(mqtt_broker_ip, mqtt_broker_port, siteId))
    siteProcs.append(sp)
    sp.start()
    commBusClient.publish(con.TOPIC_SITE_DEVICES_CONF + "/" + str(siteId), str(sitesConf[site]), retain=True)
    commBusClient.publish(con.TOPIC_SITE_CONF + "/" + str(siteId), str(updateInterval), retain=True)
    siteId = siteId + 1

# Start console

# Available commands
availableCommands = ["sites", "devices", "site", "site add", "site delete", "device", "device_on", "device_off", "consumption", "run scenario", "help", "exit"]
Completer = WordCompleter(availableCommands)

# Console loop
memHistory = InMemoryHistory()
while True:
    cmd = prompt(unicode(con.CONSOLE_PROMPT), history=memHistory, completer=Completer)

    if cmd in availableCommands: 
        if cmd == "exit" :
            print("'There is a kind of senity in love which is almost a paradise'")
            break
        elif cmd == "help" :
            print("Available commands: " + str(availableCommands))
        elif cmd == "sites":
            foundSites = []
            commBusClient.subscribe(con.TOPIC_SITE_CONF + "/#")
            time.sleep(2)
            print foundSites
    else:
        print("Command not found")

# Close senity
closeSenity(siteProcs)
