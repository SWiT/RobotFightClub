import time, math, serial, re, os
from utils import *


class Bot:
    used_sdi = []   #used serial device indexes
    
    def __init__(self, idx, serialdevices):
        self.id = idx
        self.zid = 0
        self.locZonePx = (0,0)
        self.locZone = (0,0)
        self.locArena = (0,0)
        self.heading = 0
        self.ledPt = None
        self.symbol = None
        self.alive = False
        self.time = time.time()
        self.color_dead = (0,0,255)
        self.color_alive = (0,170,0)
        self.color_detected = (29,227,245)
        self.color_roi = (127,127,127)
        
        self.serialdevices = serialdevices

        self.sdi = -1
        self.serialdevname = None
        self.serial = None  #serial connection object
        self.baudrate=115200
        return

    
    def getSerialdevices(self):
        #Get lists ofserial devices
        serial_pattern = re.compile('^rfcomm(\d)$')
        for dev in os.listdir('/dev/'):
            match = serial_pattern.match(dev)
            if match:
                self.serialdevices.append('/dev/'+dev)


    def setData(self, symbol, z, threshImg):
        self.time = time.time()
        self.symbol = symbol
        self.zid = z.id

        #update the bot's location
        self.locZonePx = findCenter(self.symbol)
        wallCenterX = findCenter([z.corners[1].location, z.corners[0].location])
        wallCenterY = findCenter([z.corners[3].location, z.corners[0].location])
        maxX = z.corners[1].location[0] - z.corners[0].location[0]
        maxY = z.corners[3].location[1] - z.corners[0].location[1]
        if abs(maxX) > 0 and abs(maxY) > 0:
            zoneX = int(float(self.locZonePx[0]-wallCenterY[0])/float(maxX)*z.actualsize[0])
            zoneY = int(float(self.locZonePx[1]-wallCenterX[1])/float(maxY)*z.actualsize[1])
            self.locZone = (zoneX, zoneY)
            #set Arena location
            self.locArena = (self.locZone[0] + (72 * z.id), self.locZone[1])
            
        #update the bot's heading
        x = self.symbol[3][0] - self.symbol[0][0]
        y = self.symbol[0][1] - self.symbol[3][1]
        h = math.degrees(math.atan2(y,x))
        if h < 0: h = 360 + h
        self.heading = int(round(h,0))
        
        #determine the bot's alive or dead status
        pt0 = self.symbol[0]
        pt2 = self.symbol[2]
        pt3 = self.symbol[3]
        x = int((pt2[0] - pt3[0])*.33 + pt3[0])
        y = int((pt2[1] - pt3[1])*.33 + pt3[1])
        x += int((pt3[0] - pt0[0])*.24)
        y += int((pt3[1] - pt0[1])*.24)
        self.ledPt = (x, y)
        roi = threshImg[y-5:y+6,x-5:x+6]
        scAvg = cv2.mean(roi)
        self.alive = scAvg[0] >= 10 
        return
    
    def drawOutput(self, outputImg):
        x,y = self.ledPt
        cv2.rectangle(outputImg, (x+5,y+5), (x-5,y-5), self.color_roi)
        
        drawBorder(outputImg, self.symbol, self.color_detected, 2)
                     
        x,y = self.locZonePx
        cv2.putText(outputImg, str(self.id), (x-8, y+8), cv2.FONT_HERSHEY_PLAIN, 1.5, self.color_detected, 2)
        
        ptdiff = findDiffs(self.symbol[1], self.symbol[2])
        pt0 = findCenter([self.symbol[2], self.symbol[3]])
        pt1 = (pt0[0]+int(ptdiff[0]*1.20), pt0[1]+int(ptdiff[1]*1.20))
        cv2.line(outputImg, pt0, pt1, self.color_detected, 2)
        return
        
    def drawLastKnownLoc(self, outputImg):
        x,y = self.locZonePx
        if x == 0 and y == 0:
            return
        if self.alive:
            color = self.color_alive
        else:
            color = self.color_dead
        cv2.circle(outputImg, (x,y), 30, color, 2)
        cv2.putText(outputImg, str(self.id), (x-8, y+8), cv2.FONT_HERSHEY_PLAIN, 1.5, color, 2)
        ang = self.heading*(math.pi/180) #convert back to radians
        pt0 = ((x+int(math.cos(ang)*30)), (y-int(math.sin(ang)*30)))
        pt1 = ((x+int(math.cos(ang)*30*3.25)), (y-int(math.sin(ang)*30*3.25)))
        cv2.line(outputImg, pt0, pt1, color, 2)
        return
        
    def nextAvailableDevice(self):
        self.sdi += 1
        if self.sdi >= len(self.serialdevices):
            self.sdi = -1
        if self.sdi != -1:
            try:
                self.used_sdi.index(self.sdi)
            except ValueError:
                return
            self.nextAvailableDevice()
        return
        
    def updateSerialDevice(self):
        if self.sdi != -1:
            self.closeSerialDevice()
        self.getSerialdevices()
        self.nextAvailableDevice()
        if self.sdi != -1:
            self.initSerialDevice()
        return
        
    def initSerialDevice(self):
        self.serialdevname = self.serialdevices[self.sdi]
        self.serial = serial.Serial(port=self.serialdevname, baudrate=self.baudrate, timeout=100)
        self.used_sdi.append(self.sdi)
        return
        
    def closeSerialDevice(self):
        self.serial.close()
        self.serialdevname = None
        try:
            self.used_sdi.remove(self.sdi)
        except ValueError:
            pass
        return
        
        
