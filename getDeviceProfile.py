import json
import os

# get device profile
def getDeviceProfile(device_file):

    with open(device_file) as json_file:
        json_data = json.load(json_file)

    return json_data

# get all device profile
def getAllDeviceProfiles(device_folder):

    allDeviceProfiles = {}

    allDeviceFiles = os.listdir(device_folder)
    
    for df in allDeviceFiles:
        dp = getDeviceProfile(device_folder + "/" + df)
        allDeviceProfiles[dp["name"]] = dp

    return allDeviceProfiles
        
#device_file = "devices/oven01.json"
#devices_folder = "devices"
#print getAllDeviceProfiles(devices_folder)['fridge01']
