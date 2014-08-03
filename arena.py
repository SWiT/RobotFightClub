import re, os
import bot
import zone

class Arena:    
    def __init__(self):
        self.numzones = 1    #number of Zones
        self.numpoi = 4      #number of POI
        self.numbots = 2     #number of bots
        self.x = 0           #maximum X value
        self.y = 0           #maximum Y value
        self.zone = []
        self.bot = []
        self.gameon = False
        self.videodevices = []
        self.serialdevices = []
        self.corners = [(-1,-1),(-1,-1),(-1,-1),(-1,-1)]
        self.threshold = 150
        
        #Get lists of video and BT devices
        video_pattern = re.compile('^video(\d)$')
        serial_pattern = re.compile('^rfcomm(\d)$')
        for dev in os.listdir('/dev/'):
            match = video_pattern.match(dev)
            if match:
                self.videodevices.append('/dev/'+dev)
            match = serial_pattern.match(dev)
            if match:
                self.serialdevices.append('/dev/'+dev)     
        if len(self.videodevices) == 0:
            raise SystemExit('No video device found. (/dev/video#)')
        self.videodevices.sort()  
        self.serialdevices.sort()
        print self.serialdevices
        self.buildZones()
        self.buildBots()
        return
        
    def updateNumberOfZones(self):
        self.numzones += 1
        if self.numzones > len(self.videodevices):
            self.numzones = 1
        self.buildZones()
        return self.numzones
        
    def buildZones(self):
        self.numpoi = (self.numzones * 4) #total number of poi in the arena
        for z in self.zone:
            z.close()
            z.used_vdi = []
        self.zone = []
        for idx in range(0,self.numzones):
            z = zone.Zone(idx, self.numzones, self.numpoi, self.videodevices)
            self.zone.append(z)
  
    def updateNumBots(self):
        self.numbots += 1
        if self.numbots > 4:
            self.numbots = 0
        self.buildBots()
        return self.numbots
    
    def buildBots(self):
        self.bot = []
        for idx in range(0,self.numbots):
            self.bot.append(bot.Bot(idx, self.serialdevices))
        return
    
    def toggleGameOn(self):
        self.gameon = False if self.gameon else True
        return
        
    def setThreshold(self, v):
        self.threshold = v
        return

