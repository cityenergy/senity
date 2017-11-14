'''
 The overall simulation Manager, which is responsible for starting and configuring the various entities
'''

import simAllInOneSite
import constants as con
import utils.getScenarioConf
import utils.getDeviceProfile
import utils.getSiteProfile

import sys
import paho.mqtt.client as mqtt
import multiprocessing
import ConfigParser
import argparse
import logging
import time
import socket

class simulationManager:

    def __init__(self):
        self.commBusClient = mqtt.Client()
        self.senityLogger = 0
        self.devices_folder = ""
        self.sites_folder = ""
        self.mqtt_broker_ip = ""
        self.mqtt_broker_port = 0
        self.websocket_broker_port = 0
        self.log_file = ""
        self.sites = []
        self.siteIds = []
        self.currentTime = 0
        self.siteProcs = []

    # Start simulation Manager
    def start(self, scenario_file, devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file):

        # Configuration paramaters
        self.devices_folder = devices_folder 
        self.sites_folder = sites_folder
        self.mqtt_broker_ip = mqtt_broker_ip
        self.mqtt_broker_port = mqtt_broker_port  
        self.websocket_broker_port = websocket_broker_port 
        self.log_file = log_file

        # Init logging
        self.__initLogging()

        # read devices and sites profiles and simulation scenarion configuration
        try:
            allDevices = utils.getDeviceProfile.getAllDeviceProfiles(self.devices_folder)
            allSites = utils.getSiteProfile.getAllSiteProfiles(self.sites_folder)
        except Exception:
            self.senityLogger.error("Device and/or site profiles could not be loaded.")
            sys.exit(0)

        try:
            (deviceUpdateInterval, simUpdateInterval, simDuration, simStartTime,  scenarioConf) = utils.getScenarioConf.getSimScenarioConf(scenario_file)
        except Exception:
            self.senityLogger.error("Scenario configuration could not be loaded.")
            sys.exit(0)

        self.currentTime = simStartTime

        # Check connectivity to communication bus 
        self.__checkMqttBrokerStatus()

        # Connect to comm bus
        self.__connectToCommBus()

        # validate data and return sites configuration
        sitesConf = self.__validateFormatScenario(scenarioConf, allSites, allDevices)

        # Create simulated "all in one" sites
        siteId = 0
        for site in sitesConf.keys():
            sp = simAllInOneSite.simAllInOneSite(siteId, sitesConf[site], deviceUpdateInterval)
            self.siteProcs.append(sp)
            self.siteIds.append(siteId)
            siteId = siteId + 1

        # The main simulation loop
        while self.currentTime <= simDuration:

            # Loop through all sites and get consumption
            for site in self.siteProcs:
                site.getConsumption(self.currentTime)

            # progress time
            self.currentTime = self.currentTime + simUpdateInterval
            print self.currentTime


    # Init logging functionallity
    def __initLogging (self):
        if not self.log_file:
            logging.propagate = False
        else:
            self.senityLogger = logging.getLogger("senity_simulationManager")
            logging.basicConfig(format='%(asctime)s : %(message)s', filename=self.log_file,level=logging.DEBUG)

    # Check that profiles and configuration data are valid and return ready format configuration to send to each site
    def __validateFormatScenario (self, scenarioConf, allSites, allDevices) :
        sitesConf = {}
        sId = 0
        for site in scenarioConf:
            dId = 0
            if not allSites.has_key(site):
                self.senityLogger.error("Site name '" + str(site) +"' not found, check configurations")
                sys.exit(0)
            sitesConf[site + "_" + str(sId)] = {}
            for device in allSites[site]:
                if not allDevices.has_key(device):
                    self.senityLogger.error("Device name '" + device +"' not found, check configurations")
                    sys.exit(0)
                sitesConf[site + "_" + str(sId)][dId]=allDevices[device]
                dId = dId + 1
            sId = sId + 1
        return sitesConf

    # The callback for when the client receives a CONNACK response from the mqtt broker
    def __on_connect(self, client, userdata, flags, rc):

        self.senityLogger.info("Simulation Manager connected on mqtt broker with result code: " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect othen subscriptions will be renewed

    # The callback for when one of the topic messages is received from the mqtt broker
    def __on_message(self, client, userdata, msg):

        pass

    # Connect to the communication bus
    def __connectToCommBus(self, userdata="") :

        # Create, configure mqtt client and connect
        self.commBusClient.loop_start()
        self.commBusClient.on_connect = self.__on_connect
        self.commBusClient.on_message = self.__on_message

        try:
            rc = self.commBusClient.connect(self.mqtt_broker_ip, self.mqtt_broker_port, 60)
        except Exception:
            self.senityLogger.error("Error while connecting to communication bus. Check whether the respective service is running.")
            print("Error while connecting to communication bus. Check whether the respective service is running.")
            sys.exit(0)

    # Check that mqtt broker is up and running
    def __checkMqttBrokerStatus(self):
        sMqtt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sMqtt.connect((str(self.mqtt_broker_ip), int(self.mqtt_broker_port)))
        except Exception as e:
            self.senityLogger.error("Error while connecting to communication bus. Check whether the respective entity is running.")
            print("Error while connecting to communication bus. Check whether the respective entity is running.")
            sys.exit(0)
        finally:
            sMqtt.close()

        sWebsocket = socket.socket()
        try:
            sWebsocket.connect((str(self.mqtt_broker_ip), int(self.websocket_broker_port)))
        except Exception as e:
            self.senityLogger.error("Websocket support is not enabled in the mqtt broket. Senity's UI functionallity will not operate normally.")
            print("Websocket support is not enabled in the mqtt broket. Senity's UI functionallity will not operate normally.")
        finally:
            sWebsocket.close()

    # Closing and exiting simulation Manager
    def closeSenity(self):
        pass

