import re, os, cv2, time, re
from numpy import *

import bot, zone, ui, dm
from utils import *

class Arena:    
    def __init__(self):
        self.numzones = 1    #number of Zones
        self.numbots = 2     #number of bots
        self.x = 0           #maximum X value
        self.y = 0           #maximum Y value
        self.zone = []
        self.bot = []
        self.gameon = False
        self.videodevices = []
        self.serialdevices = []
        self.threshold = 219
        self.allImg = None
        self.botPattern = re.compile('^(\d{2})$')
        self.cornerPattern = re.compile('^C(\d)$')
        
        #Get lists of video and serial devices
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
        #print self.serialdevices
        self.buildZones()
        self.buildBots()
        
        self.ui = ui.UI()
        self.dm = dm.DM(self.numbots + 6, 100)
        return
        
    def updateNumberOfZones(self):
        self.numzones += 1
        if self.numzones > len(self.videodevices):
            self.numzones = 1
        self.buildZones()
        return self.numzones
        
    def buildZones(self):
        for z in self.zone:
            z.close()
            z.used_vdi = []
        self.zone = []
        for idx in range(0,self.numzones):
            self.zone.append(zone.Zone(idx, self.videodevices))
  
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
        
    def deepScan(self):
        for z in self.zone:
            z.getImage()
        
            #Apply image transformations
            threshImg = cv2.cvtColor(z.image, cv2.COLOR_BGR2GRAY) #convert to grayscale
            ret,threshImg = cv2.threshold(threshImg, self.threshold, 255, cv2.THRESH_BINARY)
            
            #Start Output Image
            if self.ui.isDisplayed(z.id):
                if self.ui.displayMode >= 2:
                    outputImg = zeros((height, width, 3), uint8) #create a blank image
                elif self.ui.displayMode == 0:
                    outputImg = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2BGR)
                else:
                    outputImg = z.image;
                
            #Scan for DataMatrix
            self.dm.scan(z.image)
        
            #For each detected DataMatrix symbol
            for content,symbol in self.dm.symbols:
                #Zone Corners
                match = self.cornerPattern.match(content)
                if match:
                    sval = int(match.group(1))
                    for idx,corner in enumerate(z.corners):
                        if sval == corner.symbolvalue:
                            corner.location = symbol[idx]
                            corner.symbolcenter = findCenter(symbol)
                            
                            offset = int(corner.gap * (symbol[1][0]-symbol[0][0]) / corner.symboldimension)
                            offset_x_sign = 1 if (idx%3 != 0) else -1
                            offset_y_sign = 1 if (idx < 2) else -1
                            
                            corner.location = (corner.location[0] + offset_x_sign * offset, corner.location[1] + offset_y_sign * offset)
                            
                            corner.time = time.time()
                            if self.ui.isDisplayed(z.id) and self.ui.displayMode < 3:
                                drawBorder(outputImg, symbol, self.ui.COLOR_BLUE, 2)
                                pt = (symbol[1][0]-35, symbol[1][1]-25)  
                                cv2.putText(outputImg, str(sval), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, self.ui.COLOR_BLUE, 2)
                
                #Bot Symbol
                match = self.botPattern.match(content)
                if match:
                    botId = int(match.group(1))
                    if botId < 0 or self.numbots <=botId:
                        continue
                    bot = self.bot[botId]
                    bot.setData(symbol, z, threshImg)    #update the bot's data
                    if self.ui.isDisplayed(z.id) and self.ui.displayMode < 3:
                        bot.drawOutput(outputImg)   #draw the bot's symbol
        
            
            #Draw Objects on Scanner window if this zone is displayed
            if self.ui.isDisplayed(z.id):
                #Crosshair in center
                pt0 = (z.width/2, z.height/2-5)
                pt1 = (z.width/2, z.height/2+5)
                cv2.line(outputImg, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                pt0 = (z.width/2-5, z.height/2)
                pt1 = (z.width/2+5, z.height/2)
                cv2.line(outputImg, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                
                #Zone edges
                corner_pts = []
                for corner in z.corners:
                    #print corner.location
                    corner_pts.append(corner.location)
                #print corner_pts
                drawBorder(outputImg, corner_pts, self.ui.COLOR_BLUE, 2)
                
        
                #Last Known Bot Locations
                for bot in self.bot:
                    if bot.zid == z.id:                
                        bot.drawLastKnownLoc(outputImg)
            
            #Merge images if Display: All
            if self.ui.display == -1:
                if self.allImg is None or z.id == 0: #not set or first
                    self.allImg = zeros((z.height, z.width*self.numzones, 3), uint8)
                #print z.id, z.height, z.width, self.numzones, size(outputImg,0), size(outputImg,1)
                if size(outputImg,0) == z.height and size(outputImg,1) == z.width:
                    self.allImg[0:z.height, (z.id*z.width):((z.id+1)*z.width)] = outputImg
                if z.id+1 == len(self.zone):   #last
                    outputImg = self.allImg
        
        #End of zone loop
        return outputImg
        

