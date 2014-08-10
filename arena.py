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
            
    def deepScan(self):
        for bot in self.bot:
            bot.found = False
            
        for z in self.zone:
            z.getImage()
        
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
                            corner.symbol = symbol
                            corner.location = symbol[idx]
                            corner.symbolcenter = findCenter(symbol)
                            
                            offset = int(corner.gap * (symbol[1][0]-symbol[0][0]) / corner.symboldimension)
                            offset_x_sign = 1 if (idx%3 != 0) else -1
                            offset_y_sign = 1 if (idx < 2) else -1
                            
                            corner.location = (corner.location[0] + offset_x_sign * offset, corner.location[1] + offset_y_sign * offset)
                            corner.time = time.time()
                            corner.found = True
                            
                #Bot Symbol
                match = self.botPattern.match(content)
                if match:
                    botId = int(match.group(1))
                    if botId < 0 or self.numbots <=botId:
                        continue
                    bot = self.bot[botId]
                    bot.setData(symbol, z)    #update the bot's data
                    bot.found = True

        #End of zone loop
        return


    def render(self):
        #Start Output Image
        #create a blank image
        if self.ui.displayAll():
            widthAll = 0
            heightAll = 0
            for z in self.zone:
                widthAll += z.width
                heightAll = z.height
            outputImg = zeros((heightAll, widthAll, 3), uint8)
        elif size(self.zone) > 0:
            print self.ui.display
            print self.zone
            outputImg = zeros((self.zone[self.ui.display].height, self.zone[self.ui.display].width, 3), uint8)
        else:
            outputImg = zeros((720, 1280, 3), uint8)
        
        for z in self.zone:
            if self.ui.isDisplayed(z.id):
                if self.ui.displayMode == 0:
                    img = cv2.cvtColor(z.imageThresh, cv2.COLOR_GRAY2BGR)
                elif self.ui.displayMode >= 2:
                    img = zeros((z.height, z.width, 3), uint8) #create a blank image
                else:
                    img = z.image
                    
                #Draw Objects on Scanner window if this zone is displayed
                #Crosshair in center
                pt0 = (z.width/2, z.height/2-5)
                pt1 = (z.width/2, z.height/2+5)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                pt0 = (z.width/2-5, z.height/2)
                pt1 = (z.width/2+5, z.height/2)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                
                #Zone edges
                corner_pts = []
                for corner in z.corners:
                    corner_pts.append(corner.location)
                    if self.ui.displayMode < 3 and corner.found:
                        drawBorder(img, corner.symbol, self.ui.COLOR_BLUE, 2)
                        pt = (corner.symbolcenter[0]-5, corner.symbolcenter[1]+5)  
                        cv2.putText(img, str(corner.symbolvalue), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, self.ui.COLOR_BLUE, 2)
                drawBorder(img, corner_pts, self.ui.COLOR_BLUE, 2)
                
                #Last Known Bot Locations
                for bot in self.bot:
                    if bot.zid == z.id:                
                        bot.drawLastKnownLoc(img)
                        if self.ui.displayMode < 3 and bot.found:
                            bot.drawOutput(img)   #draw the detection symbol
                        
                if self.ui.displayAll():
                    outputImg[0:z.height, z.id*z.width:(z.id+1)*z.width] = img
                else:
                    outputImg = img
                        
        return outputImg

