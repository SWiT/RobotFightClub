import cv2, serial, sys, math, time, subprocess, os, re, Image
from numpy import *
from pydmtx import DataMatrix
import arena
from utils import *

###############
## FUNCTIONS
###############
            
def updateTimeout(v):
    global dm_timeout, dm_read
    dm_timeout = v
    dm_read = DataMatrix(max_count = dm_max, timeout = dm_timeout, shape = DataMatrix.DmtxSymbol10x10)
    return
    
def updateDisplayMode():
    global displayMode
    displayMode += 1
    if displayMode > 3:
        displayMode = 0
    return

def updateThreshold(v):
    global threshold
    threshold = v
    return

def updateDisplay(v = None):
    global display, Arena
    if v is not None:
        display = v
    else:
        display += 1
        if display >= Arena.numzones:
            display = -1
    return
    

def updateDisplaySize():
    global displaySize
    displaySize += 25
    if displaySize > 100:
        displaySize = 25
    return
        
#Insert an empty row into the ArenaControlPanel menu    
def menuSpacer():
    global menurows, cppt, cplh
    menurows.append("space")
    cppt = (cppt[0],cppt[1]+cplh)
    
def onMouse(event,x,y,flags,param):
    #if flags == 1: print event,x,y,flags,param
    #print cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN, cv2.EVENT_MBUTTONDOWN
    #print cv2.EVENT_LBUTTONUP, cv2.EVENT_RBUTTONUP, cv2.EVENT_MBUTTONUP
    #print cv2.EVENT_LBUTTONDBLCLK, cv2.EVENT_RBUTTONDBLCLK, cv2.EVENT_MBUTTONDBLCLK
    global cplh, menurows, exit, dm_max, dm_read, dm_timeout, display
    if event == cv2.EVENT_LBUTTONUP and flags == 1:
        rowClicked = y/cplh
        if rowClicked < len(menurows):
            if menurows[rowClicked] == "zones":
                Arena.updateNumberOfZones()
                display = 0
                
            elif menurows[rowClicked] == "exit":
                exit = True
                
            elif menurows[rowClicked] == "gameon":
                Arena.toggleGameOn()
                
            elif menurows[rowClicked] == "displaymode":
                updateDisplayMode()
                
            elif menurows[rowClicked] == "display":
                if x <= 150:
                    updateDisplay()
                else:
                    updateDisplaySize()
                
            elif menurows[rowClicked] == "numbots":
                Arena.updateNumBots()
                dm_max = Arena.numbots + Arena.numpoi
                dm_read = DataMatrix(max_count = dm_max, timeout = dm_timeout, shape = DataMatrix.DmtxSymbol10x10)
        
            else:    
                videoDevice_pattern = re.compile('^videoDevice(\d)$')
                match = videoDevice_pattern.match(menurows[rowClicked])
                if match:
                    zidx = int(match.group(1))
                    if x <= 28:
                        updateDisplay(zidx)
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

###############
## SETUP
###############

Arena = arena.Arena()

#Control Panel
cph = 640 #control panel height
cpw = 350 #control panel width
cplh = 20 #control panel line height
cppt = (0,cplh) #control panel current text output position    
menurows = []

cv2.namedWindow("ArenaScanner")
cv2.namedWindow("ArenaControlPanel")
cv2.startWindowThread()

display = 0
displaySize = 100
displayMode = 1
allImg = None
colorCode = ((255,0,0), (0,240,0), (0,0,255), (29,227,245), (224,27,217), (127,127,127)) #Blue, Green, Red, Yellow, Purple, Gray
threshold = 150
frametime = time.time()
fps = 0

#DataMatrix  
dm_max = Arena.numbots + Arena.numpoi; #points of interest plus the bots
dm_timeout = 200
dm_read = DataMatrix(max_count = dm_max, timeout = dm_timeout, shape = DataMatrix.DmtxSymbol10x10)

#Control Panel
cv2.createTrackbar('Scan (ms)', 'ArenaControlPanel', dm_timeout, 1000, updateTimeout)
cv2.createTrackbar('Threshold', 'ArenaControlPanel', threshold, 255, updateThreshold)
 
poi_pattern = re.compile('^C(\d)$')
bot_pattern = re.compile('^(\d{2})$')

cv2.setMouseCallback("ArenaControlPanel", onMouse)

exit = False

###############
## LOOP
###############
while True:
    for z in Arena.zone:
        #skip if capture is disabled
        if z.cap == -1:
            continue
            
        #get the next frame from the zones capture device
        success, origImg = z.cap.read()
        if not success:
            print("Error reading from camera: "+str(z.vdi));
            exit = True
            break;
        width = size(origImg, 1)
        height = size(origImg, 0)

        #Apply image transformations
        threshImg = cv2.cvtColor(origImg, cv2.COLOR_BGR2GRAY) #convert to grayscale
        ret,threshImg = cv2.threshold(threshImg, threshold, 255, cv2.THRESH_BINARY)
        
        #Start Output Image
        if display == z.id or display == -1:
            if displayMode >= 2:
                outputImg = zeros((height, width, 3), uint8) #create a blank image
            elif displayMode == 0:
                outputImg = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2BGR)
            else:
                outputImg = origImg;
            
        #Scan for DataMatrix
        dm_read.decode(width, height, buffer(origImg.tostring()))  

        #For each detected DataMatrix symbol
        for dm_idx in range(1, dm_read.count()+1):
            symbol = dm_read.stats(dm_idx)
            
            #Arena POI/Corners
            match = poi_pattern.match(symbol[0])
            if match:
                sval = int(match.group(1))
                for idx,poival in enumerate(z.poisymbol):
                    if sval == poival:
                        z.poi[idx] = symbol[1][idx]
                        z.poitime[idx] = time.time()
                        if (display == z.id or display == -1) and displayMode < 3:
                            drawBorder(outputImg, symbol[1], colorCode[0], 2)
                            pt = (symbol[1][1][0]-35, symbol[1][1][1]-25)  
                            cv2.putText(outputImg, str(idx), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[0], 2)
            
            #Bot Symbol
            match = bot_pattern.match(symbol[0])
            if match:
                botId = int(match.group(1))
                if botId < 0 or Arena.numbots <=botId:
                    continue
                bot = Arena.bot[botId]
                
                #update the bot's data
                bot.setData(symbol[1], z, threshImg)

                #draw the bot's symbol
                if (display == z.id or display == -1) and displayMode < 3:
                    bot.drawOutput(outputImg)

        #Draw Objects on Scanner window if this zone is displayed
        if display == z.id or display == -1:
            #Crosshair in center
            pt0 = (width/2,height/2-5)
            pt1 = (width/2,height/2+5)
            cv2.line(outputImg, pt0, pt1, colorCode[4], 1)
            pt0 = (width/2-5,height/2)
            pt1 = (width/2+5,height/2)
            cv2.line(outputImg, pt0, pt1, colorCode[4], 1)
            
            #Zone edges
            drawBorder(outputImg, z.poi, colorCode[0], 2)  

            #Last Known Bot Locations
            for bot in Arena.bot:
                pt = bot.locZonePx
                if pt[0] == 0 and pt[1] == 0:
                    continue
                if bot.alive:
                    color = colorCode[3]
                else:
                    color = colorCode[2]
                cv2.circle(outputImg, pt, 30, color, 2)
                textPt = (pt[0]-8, pt[1]+8)
                cv2.putText(outputImg, str(bot.id), textPt, cv2.FONT_HERSHEY_PLAIN, 1.5, color, 2)
                ang = bot.heading*(math.pi/180) #convert back to radians
                pt0 = ((pt[0]+int(math.cos(ang)*30)), (pt[1]-int(math.sin(ang)*30)))
                pt1 = ((pt[0]+int(math.cos(ang)*30*3.25)), (pt[1]-int(math.sin(ang)*30*3.25)))
                cv2.line(outputImg, pt0, pt1, color, 2)
        
        #Merge images if Display: All
        if display == -1:
            if allImg is None or z.id == 0: #not set or first
                allImg = zeros((height, width*Arena.numzones, 3), uint8)
                
            allImg[0:height, (z.id*width):((z.id+1)*width)] = outputImg
            if z.id+1 == len(Arena.zone):   #last
                outputImg = allImg
                           
    #########################################################

    #Draw Control Panel
    cph = len(menurows)*cplh+5 #calculate window height
    controlPanelImg = zeros((cph,cpw,3), uint8) #create a blank image for the control panel
    cppt = (0,cplh) #current text position  
    menutextcolor = (255,255,255)
    menurows = []
        
    #Display Zones, video devices, and resolutions
    output = "Zones: "+str(Arena.numzones)
    cv2.putText(controlPanelImg, output, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("zones")
    cppt = (cppt[0],cppt[1]+cplh)
    for z in Arena.zone:
        output = str(z.id)+": "
        cv2.putText(controlPanelImg, output, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        output = z.videodevices[z.vdi][5:] if z.vdi > -1 else "Off"
        cv2.putText(controlPanelImg, output, (cppt[0]+28,cppt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        output = str(z.resolutions[z.ri][0])+"x"+str(z.resolutions[z.ri][1])
        cv2.putText(controlPanelImg, output, (cppt[0]+125,cppt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        output = "settings"
        cv2.putText(controlPanelImg, output, (cppt[0]+270,cppt[1]-2), cv2.FONT_HERSHEY_PLAIN, 1.0, menutextcolor, 1)
        menurows.append("videoDevice"+str(z.id))
        cppt = (cppt[0],cppt[1]+cplh)
    
    menuSpacer()
        
    #Display
    output = "Display: "+str(display) if display>-1 else "Display: All"
    cv2.putText(controlPanelImg, output, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    #Display Size
    output = "Size: "+str(displaySize)+"%"
    cv2.putText(controlPanelImg, output, (cppt[0]+150,cppt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("display")
    cppt = (cppt[0],cppt[1]+cplh)
    
    #Display Mode Labels
    displayModeLabel = "Mode: "      
    if displayMode == 0: #display source image
        displayModeLabel += "Threshold"   
    elif displayMode == 1: #display source with data overlay
        displayModeLabel += "Overlay"
    elif displayMode == 2: #display only data overlay
        displayModeLabel += "Data Only"
    elif displayMode == 3: #display the only the bots point of view
        displayModeLabel += "Bot POV"
    cv2.putText(controlPanelImg, displayModeLabel, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    #Draw FPS
    output = "FPS: "+str(fps)
    cv2.putText(controlPanelImg, output, (cpw-105,cppt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("displaymode")
    cppt = (cppt[0],cppt[1]+cplh)
    
    menuSpacer()
    
    #Game Status
    status = "Game: On" if Arena.gameon else "Game: Off"
    cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("gameon")
    cppt = (cppt[0],cppt[1]+cplh)
    
    menuSpacer()
    
    #Number of Bots
    status = "Bots: " +str(Arena.numbots)
    cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("numbots")
    cppt = (cppt[0],cppt[1]+cplh)
        
    #Draw Bot Statuses and Settings
    for bot in Arena.bot:
        status = str(bot.id)+":"
        status += ' '+str(bot.locZone)
        status += ' '+str(bot.heading)
        status += ' '+('A' if bot.alive else 'D')
        status += ' '+str(int(round((time.time()-bot.time)*1000,0)))
        cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        menurows.append("bot"+str(bot.id))
        cppt = (cppt[0],cppt[1]+cplh)
        
        status = str(bot.serialdev)
        cv2.putText(controlPanelImg, status, (cppt[0]+25,cppt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        menurows.append("botserial"+str(bot.id))
        cppt = (cppt[0],cppt[1]+cplh)
    
    menuSpacer()
        
    #Draw Zone POI statuses
    for z in Arena.zone:
        for idx in range(0,4):
            status = "Z"+str(z.id)+" C"+str(z.poisymbol[idx])+":"
            status += ' '+str(int(round((time.time()-z.poitime[idx])*1000,0)))
            cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            menurows.append("z"+str(z.id)+"c"+str(idx))
            cppt = (cppt[0],cppt[1]+cplh)
        
    menuSpacer()
    
    #Draw Exit
    cv2.putText(controlPanelImg, "Exit", cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("exit")
    cppt = (cppt[0],cppt[1]+cplh)
    
    #############################################

    #Resize output image
    if 0 < displaySize < 100:
        r = float(displaySize)/100
        outputImg = cv2.resize(outputImg, (0,0), fx=r, fy=r)

    #Display the image or frame of video
    cv2.imshow("ArenaScanner", outputImg)
    cv2.imshow("ArenaControlPanel", controlPanelImg)

    #Calculate FPS
    fps = int(1/(time.time() - frametime))
    frametime = time.time()

    #Exit
    if exit: 
        break
      
###############
## END LOOP
###############
for z in Arena.zone:
    z.close()
cv2.destroyAllWindows()

print "Exiting."



