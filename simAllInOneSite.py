'''
 A simulated all-in-one site
'''

class simAllInOneSite:

    def __init__(self, siteId, siteDevices, updateInterval):

        self.sId = siteId        
        self.siteDevices = siteDevices
        self.updateInterval = updateInterval


    def setUpdateInterval (self, updateInterval):

        self.updateInterval = updateInterval
       

    def getConsumption (self, currentTime):
       
        return 1000;

