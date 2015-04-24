import cv2, time, re
from numpy import *

class UI:
    def __init__(self):
        self.COLOR_WHITE = (255,255,255)
        self.COLOR_BLUE = (255,0,0)
        self.COLOR_LBLUE = (255, 200, 100)
        self.COLOR_GREEN = (0,240,0)
        self.COLOR_RED = (0,0,255)
        self.COLOR_YELLOW = (29,227,245)
        self.COLOR_PURPLE = (224,27,217)
        self.COLOR_GRAY = (127,127,127)
        self.h = 640 #control panel height
        self.w = 350 #control panel width
        self.lh = 20 #control panel line height
        self.pt = (0,self.lh) #control panel current text output position    
        self.menurows = []
        self.display = 0
        self.displaySize = 50
        self.displayMode = 1
        self.numzones = 1
        self.frametime = time.time()
        self.fps = 0
        self.exit = False
        return
    
    def isDisplayed(self,idx):
        return self.display == idx or self.display == -1
        
    def displayAll(self):
        return self.display == -1
        
    def updateDisplayMode(self):
        self.displayMode += 1
        if self.displayMode > 3:
            self.displayMode = 0
        return
    
    def updateDisplay(self,v = None):
        if v is not None:
            self.display = v
        else:
            #print self.display, self.numzones
            self.display += 1
            if self.display >= self.numzones:
                self.display = -1
        return
    
    def updateDisplaySize(self):
        self.displaySize += 10
        if self.displaySize > 100:
            self.displaySize = 50
        return
        
    def menuSpacer(self):
        self.menurows.append("space")
        self.pt = (self.pt[0],self.pt[1]+self.lh)
    
    #Calculate FPS
    def calcFPS(self):    
        self.fps = int(1/(time.time() - self.frametime))
        self.frametime = time.time()
    
    def onMouse(self,event,x,y,flags,param):
        #print "Mouse:",event,x,y,flags
        if event == cv2.EVENT_LBUTTONUP:
            Arena = param
            rowClicked = y/self.lh
            if rowClicked < len(self.menurows):
                if self.menurows[rowClicked] == "zones":
                    self.numzones = Arena.updateNumberOfZones()
                    self.updateDisplay(-1)
                    
                elif self.menurows[rowClicked] == "exit":
                    self.exit = True
                    
                elif self.menurows[rowClicked] == "gameon":
                    Arena.toggleGameOn()
                    
                elif self.menurows[rowClicked] == "displaymode":
                    self.updateDisplayMode()
                    
                elif self.menurows[rowClicked] == "display":
                    if x <= 150:
                        self.updateDisplay()
                    else:
                        self.updateDisplaySize()
                    
                elif self.menurows[rowClicked] == "numbots":
                    Arena.updateNumBots()
                        
                else:    
                    videoDevice_pattern = re.compile('^videoDevice(\d)$')
                    match = videoDevice_pattern.match(self.menurows[rowClicked])
                    if match:
                        zidx = int(match.group(1))
                        if x <= 28:
                            self.updateDisplay(zidx)
                        elif x <= 125:
                            Arena.zone[zidx].updateVideoDevice()
                        elif x <= 275:
                            Arena.zone[zidx].updateResolution()
                        else:
                            if Arena.zone[zidx].v4l2ucp != -1:
                                Arena.zone[zidx].closeV4l2ucp()
                            else:
                                Arena.zone[zidx].openV4l2ucp()
                        return
                        
                    botserial_pattern = re.compile('^botserial(\d)$')
                    match = botserial_pattern.match(self.menurows[rowClicked])
                    if match:
                        bidx = int(match.group(1))
                        Arena.bot[bidx].updateSerialDevice()
                        return

        return
    
    def nextrow(self):
        self.pt = (self.pt[0],self.pt[1]+self.lh)
        return
        
    def drawControlPanel(self, Arena):
        #Draw Control Panel
        self.pt = (0,self.lh)
        self.h = len(self.menurows)*self.lh+5 #calculate window height
        controlPanelImg = zeros((self.h,self.w,3), uint8) #create a blank image for the control panel
        menutextcolor = (255,255,255)
        self.menurows = []
            
        #Display Zones, video devices, and resolutions
        output = "Zones: "+str(Arena.numzones)
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("zones")
        self.nextrow()
        for z in Arena.zone:
            output = str(z.id)+": "
            cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            output = z.videodevices[z.vdi][5:] if z.vdi > -1 else "Off"
            cv2.putText(controlPanelImg, output, (self.pt[0]+28,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            output = str(z.resolutions[z.ri][0])+"x"+str(z.resolutions[z.ri][1])
            cv2.putText(controlPanelImg, output, (self.pt[0]+125,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            output = "settings"
            cv2.putText(controlPanelImg, output, (self.pt[0]+270,self.pt[1]-2), cv2.FONT_HERSHEY_PLAIN, 1.0, menutextcolor, 1)
            self.menurows.append("videoDevice"+str(z.id))
            self.nextrow()
        
        self.menuSpacer()
            
        #Display
        output = "Display: "+str(self.display) if self.display>-1 else "Display: All"
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        #Display Size
        output = "Size: "+str(self.displaySize)+"%"
        cv2.putText(controlPanelImg, output, (self.pt[0]+150,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("display")
        self.nextrow()
        
        #Display Mode Labels
        output = "Mode: "      
        if self.displayMode == 0: #display source image
            output += "Threshold"   
        elif self.displayMode == 1: #display source with data overlay
            output += "Overlay"
        elif self.displayMode == 2: #display only data overlay
            output += "Data Only"
        elif self.displayMode == 3: #display the only the bots point of view
            output += "Bot POV"
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        #Draw FPS
        output = "FPS: "+str(self.fps)
        cv2.putText(controlPanelImg, output, (self.w-105,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("displaymode")
        self.nextrow()
        
        self.menuSpacer()
        
        #Game Status
        output = "Game: On" if Arena.gameon else "Game: Off"
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("gameon")
        self.nextrow()
        
        self.menuSpacer()
        
        #Number of Bots
        output = "Bots: " +str(Arena.numbots)
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("numbots")
        self.nextrow()
            
        #Draw Bot Statuses and Settings
        for bot in Arena.bot:
            output = str(bot.id)+":"
            output += ' Z'+str(bot.zid)
            output += ' '+str(bot.locArena)
            output += ' '+str(bot.heading)
            output += ' '+('A' if bot.alive else 'D')
            output += ' '+str(int(round((time.time()-bot.time)*1000,0)))
            cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            self.menurows.append("bot"+str(bot.id))
            self.nextrow()
            
            output = str(bot.serialdevname)
            cv2.putText(controlPanelImg, output, (self.pt[0]+25,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            self.menurows.append("botserial"+str(bot.id))
            self.nextrow()
        
        self.menuSpacer()
            
        #Draw Zone POI statuses
        for z in Arena.zone:
            for corner in z.corners:
                output = "Z"+str(z.id)+" C"+str(corner.symbolvalue)+":"
                output += ' '+str(int(round((time.time()-corner.time)*1000,0)))
                cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
                self.menurows.append("z"+str(z.id)+"c"+str(corner.idx))
                self.nextrow()
            
        self.menuSpacer()
        
        #Draw Exit
        cv2.putText(controlPanelImg, "Exit", self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("exit")
        self.nextrow()
        
        return controlPanelImg
          
    def resize(self, img):        
        #Resize output image
        if size(img,1) > 0 and size(img,0) > 0 and 0 < self.displaySize < 100:
            r = float(self.displaySize)/100
            img = cv2.resize(img, (0,0), fx=r, fy=r)
        return img

