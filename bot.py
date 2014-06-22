import time, math
from utils import *

class Bot:
    used_serialdev = []
    
    def __init__(self, idx):
        self.id = idx
        self.locZonePx = (0,0)
        self.locZone = (0,0)
        self.locArena = (0,0)
        self.heading = 0
        self.ledPt = None
        self.symbol = None
        self.alive = False
        self.time = time.time()
        self.serialdev = None
        self.color_dead = (0,0,255)
        self.color_alive = (29,227,245)
        self.color_detected = (0,240,0)
        self.color_roi = (127,127,127)
        return
          
    def setData(self, symbol, z, threshImg):
        self.time = time.time()
        self.symbol = symbol
        
        #update the bot's location
        self.locZonePx = findCenter(self.symbol)
        wallCenterX = findCenter([z.poi[1],z.poi[0]])
        wallCenterY = findCenter([z.poi[3],z.poi[0]])
        maxX = z.poi[1][0]-z.poi[0][0]
        maxY = z.poi[3][1]-z.poi[0][1]
        if abs(maxX) > 0 and abs(maxY) > 0:
            zoneX = int(float(self.locZonePx[0]-wallCenterY[0])/float(maxX)*z.actualsize[0])
            zoneY = int(float(self.locZonePx[1]-wallCenterX[1])/float(maxY)*z.actualsize[1])
            self.locZone = (zoneX, zoneY)
            
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
        x = self.ledPt[0]
        y = self.ledPt[1]
        cv2.rectangle(outputImg, (x+5,y+5), (x-5,y-5), self.color_roi)
        
        drawBorder(outputImg, self.symbol, self.color_detected, 2)
                     
        pt = self.locZonePx
        pt = (pt[0]-8, pt[1]+8)            
        cv2.putText(outputImg, str(self.id), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, self.color_detected, 2)
        
        ptdiff = findDiffs(self.symbol[1], self.symbol[2])
        pt0 = findCenter([self.symbol[2], self.symbol[3]])
        pt1 = (pt0[0]+int(ptdiff[0]*1.20), pt0[1]+int(ptdiff[1]*1.20))
        cv2.line(outputImg, pt0, pt1, self.color_detected, 2)
        return
