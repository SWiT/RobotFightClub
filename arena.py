import re, os, subprocess, cv2, time
import bot
CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

class Arena:    
    def __init__(self):
        self.numzones = 1    #number of Zones
        self.numpoi = 4      #number of POI
        self.numbots = 1     #number of bots
        self.x = 0           #maximum X value
        self.y = 0           #maximum Y value
        self.zone = []
        self.bot = []
        self.gameon = False
        self.videodevices = []
        self.btserialdevices = []
        self.corners = [(-1,-1),(-1,-1),(-1,-1),(-1,-1)]
        
        #Get lists of video and BT devices
        video_pattern = re.compile('^video(\d)$')
        btserial_pattern = re.compile('^rfcomm(\d)$')
        for dev in os.listdir('/dev/'):
            match = video_pattern.match(dev)
            if match:
                self.videodevices.append('/dev/'+dev)
            match = btserial_pattern.match(dev)
            if match:
                self.btserialdevices.append('/dev/'+dev)     
        self.videodevices.sort()  
        self.btserialdevices.sort()
        print self.videodevices
        print self.btserialdevices
        
        self.buildZones()
        self.buildBots()
        
    def updateNumberOfZones(self):
        self.numzones += 1
        if self.numzones > len(self.videodevices):
            self.numzones = 1
        self.buildZones()
        return 
        
    def buildZones(self):
        self.numpoi = (self.numzones * 2) + 2 #number of poi
        for z in self.zone:
            z.close()
            z.used_vdi = []
        self.zone = []
        for idx in range(0,self.numzones):
            z = Zone(idx, self.numzones, self.numpoi, self.videodevices)
            self.zone.append(z)
  
    def updateNumBots(self):
        self.numbots += 1
        if self.numbots > 4:
            self.numbots = 0
        self.buildBots()
        return
    
    def buildBots(self):
        self.bot = []
        for idx in range(0,self.numbots):
            b = bot.Bot(idx)
            self.bot.append(b)
        return
    
    def toggleGameOn(self):
        self.gameon = False if self.gameon else True
        return
        
class Zone:
    used_vdi = []
    def __init__(self, idx, nzones, npoi, videodevices):
        self.id = idx
        self.vdi = idx
        self.videodevices = videodevices
        self.actualsize = (70.5, 46.5) #zone size in inches
        self.poisymbol = [-1,-1,-1,-1]
        self.poi = [(-1,-1),(-1,-1),(-1,-1),(-1,-1)]
        self.poitime = [time.time(), time.time(), time.time(), time.time()] 
        self.xoffset = 0
        self.yoffset = 0 
        self.v4l2ucp = -1
        self.cap = -1        #capture device object (OpenCV)
        self.resolutions = [(640,480),(1280,720),(1920,1080)]
        self.ri = 0          #selected Resolution Index
        self.poisymbol[0] = idx
        self.poisymbol[1] = idx + 1
        self.poisymbol[2] = npoi - idx - 2
        self.poisymbol[3] = npoi - idx - 1
        self.initVideoDevice()
        return
    
    def nextAvailableDevice(self):
        self.vdi += 1
        if self.vdi >= len(self.videodevices):
            self.vdi = -1
        if self.vdi != -1:
            try:
                self.used_vdi.index(self.vdi)
            except ValueError:
                return
            self.nextAvailableDevice()
        return
        
    def updateVideoDevice(self):
        self.close()
        self.nextAvailableDevice()
        if self.vdi != -1:
            self.initVideoDevice()
        else:
            self.close()    
        return
        
    def openV4l2ucp(self):
        self.v4l2ucp = subprocess.Popen(['v4l2ucp',self.videodevices[self.vdi]])
        return

    def closeV4l2ucp(self):
        if self.v4l2ucp != -1:
            self.v4l2ucp.kill()
            self.v4l2ucp = -1
        return
             
    def initVideoDevice(self):
        if self.vdi != -1:
            self.cap = cv2.VideoCapture(self.vdi)
            self.cap.set(CV_CAP_PROP_FRAME_WIDTH, self.resolutions[self.ri][0])
            self.cap.set(CV_CAP_PROP_FRAME_HEIGHT, self.resolutions[self.ri][1])
            self.used_vdi.append(self.vdi)          
        return
        
    def close(self):
        self.closeV4l2ucp()
        self.closeCap()
        try:
            self.used_vdi.remove(self.vdi)
        except ValueError:
            pass
        return
    
    def closeCap(self):
        if self.cap != -1: 
            self.cap.release()
            self.cap = -1
        return
        
    def updateResolution(self):
        self.ri += 1
        if self.ri >= len(self.resolutions):
            self.ri = 0
        x = self.resolutions[self.ri][0]
        y = self.resolutions[self.ri][1]
        self.close()
        self.initVideoDevice()
        self.poi = [(0,y),(x,y),(x,0),(0,0)]
        return
