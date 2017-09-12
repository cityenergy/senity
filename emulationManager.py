# The overall emulation Manager, which is responsible for starting and configuring the various entities
import getScenarioConf
import getDeviceProfile
import getSiteProfile
import allInOneSite

import sys
import paho.mqtt.client as mqtt
import multiprocessing

# check that profiles and configuration data are valid and return ready format configuration to send to each site
def validateFormatScenario (scenarioConf, allSites, allDevices) : 

    sitesConf = {}
    for site in scenarioConf:
        if not allSites.has_key(site):
            print "Site name '" + site +"' not found, check configurations"
            sys.exit(0)
        sitesConf[site] = []
        for device in allSites[site]:
            if not allDevices.has_key(device):
                print "Device name '" + device +"' not found, check configurations"
                sys.exit(0)
            sitesConf[site].append(allDevices[device])

    return sitesConf

# input settings
if len(sys.argv) != 5 :
    print "Wrong inpurt parameters: <mqtt broker ip/hostname> <devices folder> <sites folder> <scenario configuration file>"
    sys.exit(0)
else:
    mqtt_broker_ip = sys.argv[1]
    mqtt_broker_port = 1883
    devices_folder = sys.argv[2]
    sites_folder = sys.argv[3]
    scenario_file = sys.argv[4]

# read devices and sites profiles and emulation scenarion configuration
allDevices = getDeviceProfile.getAllDeviceProfiles(devices_folder)
allSites = getSiteProfile.getAllSiteProfiles(sites_folder)
scenarioConf = getScenarioConf.getScenarioConf(scenario_file)
#print devices
#print sites
#print scenarioConf

# validate data and return sites configuration
sitesConf = validateFormatScenario(scenarioConf, allSites, allDevices)

# Create emulated "all in one" sites
siteProcs = []
for site in sitesConf.keys():
    sp = multiprocessing.Process(target=allInOneSite.runSite, args=(mqtt_broker_ip, mqtt_broker_port))
    siteProcs.append(sp)
    sp.start()


# Publish configurations for each site

