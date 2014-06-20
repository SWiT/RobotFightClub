import cv2, serial, sys, math, time, subprocess, os, re, Image
from numpy import *
from pydmtx import DataMatrix
import arena

###############
## FUNCTIONS
###############
def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def findCenter(pts):
    x = 0
    y = 0
    l = len(pts)
    for i in range(0,l):
        x += pts[i][0]
        y += pts[i][1]
    return (int(x/l), int(y/l))

def findDiffs(pt0, pt1):
    x = pt1[0]-pt0[0]
    y = pt1[1]-pt0[1]
    return (x,y)

def drawBorder(img, symbol, color, thickness):
    cv2.line(img, symbol[0], symbol[1], color, thickness)
    cv2.line(img, symbol[1], symbol[2], color, thickness)
    cv2.line(img, symbol[2], symbol[3], color, thickness)
    cv2.line(img, symbol[3], symbol[0], color, thickness)
            
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



#Insert an empty row into the ArenaControlPanel menu    
def menuSpacer():
    global menurows, cppt, cplh
    menurows.append("space")
    cppt = (cppt[0],cppt[1]+cplh)
    
def onMouse(event,x,y,flags,param):
    if flags == 1: print event,x,y,flags,param
    #print cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN, cv2.EVENT_MBUTTONDOWN
    #print cv2.EVENT_LBUTTONUP, cv2.EVENT_RBUTTONUP, cv2.EVENT_MBUTTONUP
    #print cv2.EVENT_LBUTTONDBLCLK, cv2.EVENT_RBUTTONDBLCLK, cv2.EVENT_MBUTTONDBLCLK
    global cplh, menurows, exit, dm_max, dm_read, dm_timeout
    if event == cv2.EVENT_LBUTTONUP and flags == 1:
        rowClicked = y/cplh
        if rowClicked < len(menurows):
            if menurows[rowClicked] == "zones":
                Arena.updateNumberOfZones()
                
            elif menurows[rowClicked] == "exit":
                exit = True
                
            elif menurows[rowClicked] == "gameon":
                Arena.toggleGameOn()
                
            elif menurows[rowClicked] == "displaymode":
                updateDisplayMode()
                
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
                        print "SELECT THIS"
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

cv2.namedWindow("ArenaScanner")
cv2.namedWindow("ArenaControlPanel")
cv2.startWindowThread()

displayMode = 1
colorCode = ((255,0,0), (0,240,0), (0,0,255), (29,227,245), (224,27,217), (127,127,127)) #Blue, Green, Red, Yellow, Purple, Gray
threshold = 150

#DataMatrix  
dm_max = Arena.numbots + Arena.numpoi; #points of interest plus the bots
dm_timeout = 200
dm_read = DataMatrix(max_count = dm_max, timeout = dm_timeout, shape = DataMatrix.DmtxSymbol10x10)

#Control Panel
cv2.createTrackbar('Scan (ms)', 'ArenaControlPanel', dm_timeout, 1000, updateTimeout)
cv2.createTrackbar('Threshold', 'ArenaControlPanel', threshold, 255, updateThreshold)
 
poi_pattern = re.compile('^C(\d)$')

botLocAbs = [(0,0), (0,0), (0,0), (0,0)]
botLocArena = [(0,0), (0,0), (0,0), (0,0)]
botHeading = [0, 0, 0, 0]
botAlive = [False, False, False, False]
botTime = [time.time(), time.time(), time.time(), time.time()]    
bot_pattern = re.compile('^(\d{2})$')

cv2.setMouseCallback("ArenaControlPanel", onMouse)
          
exit = False

###############
## LOOP
###############
while True:
    for z in Arena.zone:
        #get the next frame from the zones capture device
        if z.cap == -1:
            continue
            
        success, origImg = z.cap.read()
        if not success:
            print("Error reading from camera: "+str(z.vdi));
            exit = True
            break;

        #Apply image transformations
        grayImg = cv2.cvtColor(origImg, cv2.COLOR_BGR2GRAY) #convert to grayscale
        ret,threshImg = cv2.threshold(grayImg, threshold, 255, cv2.THRESH_BINARY)
        width = size(origImg, 1)
        height = size(origImg, 0)
        if displayMode >= 2:
            outputImg = zeros((height, width, 3), uint8) #create a blank image
        elif displayMode == 0:
            outputImg = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2BGR)
        else:
            outputImg = origImg;
    
        #crosshair in center
        pt0 = (width/2,height/2-5)
        pt1 = (width/2,height/2+5)
        cv2.line(outputImg, pt0, pt1, colorCode[4], 1)
        pt0 = (width/2-5,height/2)
        pt1 = (width/2+5,height/2)
        cv2.line(outputImg, pt0, pt1, colorCode[4], 1)

        #Scan for DataMatrix
        dm_read.decode(width, height, buffer(origImg.tostring()))  

        #draw borders on detected symbols and record object locations
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
                        if displayMode < 3:
                            drawBorder(outputImg, symbol[1], colorCode[0], 2)
                            pt = (symbol[1][1][0]-35, symbol[1][1][1]-25)  
                            cv2.putText(outputImg, str(idx), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[0], 2)

            #Bot Symbol
            match = bot_pattern.match(symbol[0])
            if match:
                pt = findCenter(symbol[1])
                botId = int(match.group(1))
                if botId >= Arena.numbots:
                    continue

                #update botTime
                botTime[botId] = time.time();

                #update the bots location
                botLocAbs[botId] = pt
                wallCenterX = findCenter([Arena.corners[1],Arena.corners[0]])
                wallCenterY = findCenter([Arena.corners[3],Arena.corners[0]])
                maxX = Arena.corners[1][0]-Arena.corners[0][0]
                maxY = Arena.corners[3][1]-Arena.corners[0][1]
                if maxX > 0 and maxY > 0:
                    arenaPtX = int(float(pt[0]-wallCenterY[0])/float(maxX)*z.actualsize[0])
                    arenaPtY = int(float(pt[1]-wallCenterX[1])/float(maxY)*z.actualsize[1])
                    botLocArena[botId] = (arenaPtX, arenaPtY)
                    
                #update the bots heading
                x = symbol[1][3][0] - symbol[1][0][0]
                y = symbol[1][0][1] - symbol[1][3][1]
                h = math.degrees(math.atan2(y,x))
                if h < 0: h = 360 + h
                botHeading[botId] = int(round(h,0))

                #determine the bot's alive or dead status
                pt0 = symbol[1][0]
                pt2 = symbol[1][2]
                pt3 = symbol[1][3]
                x = int((pt2[0] - pt3[0])*.33 + pt3[0])
                y = int((pt2[1] - pt3[1])*.33 + pt3[1])
                x += int((pt3[0] - pt0[0])*.24)
                y += int((pt3[1] - pt0[1])*.24)
                cv2.rectangle(outputImg, (x+5,y+5), (x-5,y-5), colorCode[5])
                roi = threshImg[y-5:y+6,x-5:x+6]
                scAvg = cv2.mean(roi)
                botAlive[botId] = scAvg[0] >= 10
                

                #draw the borders, heading, and text for bot symbol
                if displayMode < 3:
                    drawBorder(outputImg, symbol[1], colorCode[1], 2)                  
                    pt = (pt[0]-15, pt[1]+10)            
                    cv2.putText(outputImg, match.group(1), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[1], 2)
                    ptdiff = findDiffs(symbol[1][1], symbol[1][2])
                    pt0 = findCenter([symbol[1][2], symbol[1][3]])
                    pt1 = (pt0[0]+int(ptdiff[0]*1.20), pt0[1]+int(ptdiff[1]*1.20))
                    cv2.line(outputImg, pt0, pt1, colorCode[1], 2)

        #Draw Objects on Scanner window
        #Arena
        drawBorder(outputImg, Arena.corners, colorCode[0], 2)  

        #Last Know Bot Locations
        for idx,pt in enumerate(botLocAbs):
            if pt[0] == 0 and pt[1] == 0:
                continue
            if botAlive[idx]:
                color = colorCode[3]
            else:
                color = colorCode[2]
            cv2.circle(outputImg, pt, 30, color, 2)
            textPt = (pt[0]-8, pt[1]+8)
            cv2.putText(outputImg, str(idx), textPt, cv2.FONT_HERSHEY_PLAIN, 1.5, color, 2)
            ang = botHeading[idx]*(math.pi/180) #convert back to radians
            pt0 = ((pt[0]+int(math.cos(ang)*30)), (pt[1]-int(math.sin(ang)*30)))
            pt1 = ((pt[0]+int(math.cos(ang)*30*3.25)), (pt[1]-int(math.sin(ang)*30*3.25)))
            cv2.line(outputImg, pt0, pt1, color, 2)

    #Draw menu on Control Panel window
    controlPanelImg = zeros((cph,cpw,3), uint8) #create a blank image for the control panel
    cppt = (0,20) #current text position  
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
        cv2.putText(controlPanelImg, output, (cppt[0]+270,cppt[1]), cv2.FONT_HERSHEY_PLAIN, 1.0, menutextcolor, 1)
        menurows.append("videoDevice"+str(z.id))
        cppt = (cppt[0],cppt[1]+cplh)
    
    menuSpacer()
        
    #Display Mode Labels
    displayModeLabel = "Display Mode: "      
    if displayMode == 0: #display source image
        displayModeLabel += "Threshold"   
    elif displayMode == 1: #display source with data overlay
        displayModeLabel += "Overlay"
    elif displayMode == 2: #display only data overlay
        displayModeLabel += "Data Only"
    elif displayMode == 3: #display the only the bots point of view
        displayModeLabel += "Bot POV"
    cv2.putText(controlPanelImg, displayModeLabel, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("displaymode")
    cppt = (cppt[0],cppt[1]+cplh)
    
    #Game Status
    status = "Game: On" if Arena.gameon else "Game: Off"
    cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("gameon")
    cppt = (cppt[0],cppt[1]+cplh)
    
    #Number of Bots
    status = "Bots: " +str(Arena.numbots)
    cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("numbots")
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
        
    #Draw Bot Statuses
    for idx in range(0,Arena.numbots):
        status = str(idx)+":"
        status += ' '+str(botLocArena[idx])
        status += ' '+str(botHeading[idx])
        status += ' '+str(int(round((time.time()-botTime[idx])*1000,0)))
        status += ' '+("Alive" if botAlive[idx] else "Dead")
        cv2.putText(controlPanelImg, status, cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        menurows.append("bot"+str(idx))
        cppt = (cppt[0],cppt[1]+cplh)
    
    #Skip a row
    menurows.append("space")
    cppt = (cppt[0],cppt[1]+cplh)
    
    #Draw Exit
    cv2.putText(controlPanelImg, "Exit", cppt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
    menurows.append("exit")
    cppt = (cppt[0],cppt[1]+cplh)
        
    
    #Display the image or frame of video
    cv2.imshow("ArenaScanner", outputImg)
    cv2.imshow("ArenaControlPanel", controlPanelImg)

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



