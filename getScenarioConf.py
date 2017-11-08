'''
   Function for reading from emulation and simulation configuration files.
'''

import json
import os

# Return data from emulation scenario configuration file
def getScenarioConf(scenario_file):

    try:
        with open(scenario_file) as json_file:
            sc = json.load(json_file)
    except Exception:
        raise Exception

    allSites = []
    for site in sc["sitesAvailable"]:
        for i in range(site["siteCounter"]):
            allSites.append(site["siteName"])

    return sc["updateInterval"], allSites

# Return data from simulation scenario configuration file
def getSimScenarioConf(scenario_file):

    try:
        with open(scenario_file) as json_file:
            sc = json.load(json_file)
    except Exception:
        raise Exception

    allSites = []
    for site in sc["sitesAvailable"]:
        for i in range(site["siteCounter"]):
            allSites.append(site["siteName"])

    return sc["updateInterval"], sc["simUpdateInterval"], sc["simDuration"], sc["simStartTime"], allSites
