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

class emulationManager:

    def __init__(self):
        self.commBusClient = mqtt.Client()
        self.senityLogger = 0
        self.devices_folder = ""
        self.sites_folder = ""
        self.mqtt_broker_ip = ""
        self.mqtt_broker_port = 0
        self.log_file = ""
        self.console_cmd_waiting = ""
        self.siteProcs = []

    # Start emulation Manager
    def start(self, conf_file, scenario_file):

        # Read configuration
        self.__readConfiguration(conf_file)

        # Init logging
        self.__initLogging()

        # read devices and sites profiles and emulation scenarion configuration
        try:
            allDevices = getDeviceProfile.getAllDeviceProfiles(self.devices_folder)
            allSites = getSiteProfile.getAllSiteProfiles(self.sites_folder)
        except Exception:
            self.senityLogger.error("Device and/or site profiles could not be loaded.")
            sys.exit(0)

        try:
            (updateInterval, scenarioConf) = getScenarioConf.getScenarioConf(scenario_file)
        except Exception:
            self.senityLogger.error("Scenario configuration could not be loaded.")
            sys.exit(0)

        # Connect to comm bus
        self.__connectToCommBus()

        # validate data and return sites configuration
        sitesConf = self.__validateFormatScenario(scenarioConf, allSites, allDevices)

        # Create emulated "all in one" sites
        siteId = 0
        for site in sitesConf.keys():
            sp = multiprocessing.Process(target=allInOneSite.startSite, args=(self.mqtt_broker_ip, self.mqtt_broker_port, siteId))
            self.siteProcs.append(sp)
            sp.start()
            self.commBusClient.publish(con.TOPIC_SITE_DEVICES_CONF + "/" + str(siteId), str(sitesConf[site]), retain=True)
            self.commBusClient.publish(con.TOPIC_SITE_CONF + "/" + str(siteId), str(updateInterval), retain=True)
            siteId = siteId + 1

    # Get communication bus / mqtt details
    def getConfParams(self):
        return self.mqtt_broker_ip, self.mqtt_broker_port, self.console_cmd_waiting

    # Init logging functionallity
    def __initLogging (self):
        if not self.log_file:
            logging.propagate = False
        else:
            self.senityLogger = logging.getLogger("senity_emulationManager")
            logging.basicConfig(format='%(asctime)s : %(message)s', filename=self.log_file,level=logging.DEBUG)

    # Read configuration parameters
    def __readConfiguration (self, conf_file):

        config = ConfigParser.ConfigParser()
        try:
            config.read(conf_file)
        except Exception:
            print("Could not read configuration file: " + conf_file)
            sys.exit(0)

        self.devices_folder = config.get('General', 'devices_folder')
        self.sites_folder = config.get('General', 'sites_folder')
        self.mqtt_broker_ip =  config.get('General', 'mqtt_broker_ip')
        self.mqtt_broker_port = config.get('General', 'mqtt_broker_port')
        self.log_file = config.get('General', 'log_file')
        console_cmd_waiting = config.get('General', 'console_cmd_waiting')

        if not console_cmd_waiting.isdigit():
            print("Error in configuration file: " + conf_file)
            sys.exit(0)
        else:
            self.console_cmd_waiting = int(console_cmd_waiting)

    # Check that profiles and configuration data are valid and return ready format configuration to send to each site
    def __validateFormatScenario (self, scenarioConf, allSites, allDevices) :

        sitesConf = {}
        for site in scenarioConf:
            dId = 0
            if not allSites.has_key(site):
                self.senityLogger.error("Site name '" + str(site) +"' not found, check configurations")
                sys.exit(0)
            sitesConf[site] = {}
            for device in allSites[site]:
                if not allDevices.has_key(device):
                    self.senityLogger.error("Device name '" + device +"' not found, check configurations")
                    sys.exit(0)
                sitesConf[site][dId]=allDevices[device]
                dId = dId + 1

        return sitesConf

    # The callback for when the client receives a CONNACK response from the mqtt broker
    def __on_connect(self, client, userdata, flags, rc):

        self.senityLogger.info("Emulation Manager connected on mqtt broker with result code: " + str(rc))

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
            self.senityLogger.error("Error while conencting to communication bus. Check whether the respective service is running.")
            print("Error while conencting to communication bus. Check whether the respective service is running.")
            sys.exit(0)

    # Closing and exiting emulation Manager
    def closeSenity(self):
        for sp in self.siteProcs:
            sp.terminate()

