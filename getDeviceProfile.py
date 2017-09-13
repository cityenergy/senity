import json
import os

# get device profile
def getDeviceProfile(device_file):

    try:
        with open(device_file) as json_file:
            json_data = json.load(json_file)
    except Exception:
        raise Exception

    return json_data

# get all device profile
def getAllDeviceProfiles(device_folder):

    allDeviceProfiles = {}

    try:
        allDeviceFiles = os.listdir(device_folder)
    except Exception:
        raise Exception
    
    for df in allDeviceFiles:
        dp = getDeviceProfile(device_folder + "/" + df)
        allDeviceProfiles[dp["name"]] = dp

    return allDeviceProfiles
        
#device_file = "devices/oven01.json"
#devices_folder = "devices"
#print getAllDeviceProfiles(devices_folder)['fridge01']
