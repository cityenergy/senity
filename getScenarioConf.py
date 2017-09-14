import json
import os

# get scenario conf
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
        
#scenario_file = "scenarios/emuScenario01.json"
#print getScenarioConf(scenario_file)
