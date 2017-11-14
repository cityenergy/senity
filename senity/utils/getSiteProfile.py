import json
import os

# get site profile
def getSiteProfile(site_file):

    with open(site_file) as json_file:
        json_data = json.load(json_file)

    return json_data

# get all site profile
def getAllSiteProfiles(site_folder):

    allSiteProfiles = {}

    allSiteFiles = os.listdir(site_folder)
    
    for sf in allSiteFiles:
        sp = getSiteProfile(site_folder + "/" + sf)
        allSiteProfiles[sp["siteName"]] = []
        for device in sp["devicesAvailable"]:
            for i in range(device["deviceCounter"]):
                 allSiteProfiles[sp["siteName"]].append(device["deviceName"])

    return allSiteProfiles
        
#sites_folder = "sites"
#print getAllSiteProfiles(sites_folder)
