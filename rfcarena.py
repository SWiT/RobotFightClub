import cv2
CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4
import serial
import sys, math, time
from numpy import *
import re
import Image
from pydmtx import DataMatrix

###############
## FUNCTIONS
###############

def displayMenu():
    print "------------------------------"
    print "'h' Print this help menu."
    print "'d' Toggle display mode."
    print "'t' Toggle verbose transmitting."
    print "'r' reset arena statuses."
    print "0-3 toggle bot alive."
    print "'v' Toggle verbose scanning."
    print "SPACE Toggles game on and off."
    print "'Esc' to exit."
    print
    
   
def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def findCenter(pts):
    x = 0
    y = 0
    for i in range(0,4):
        x += pts[i][0]
        y += pts[i][1]
    return (int(x/4), int(y/4))

def findDiffPt(pt0, pt1):
    x = int((pt0[0]+pt1[0])/2)
    y = int((pt0[1]+pt1[1])/2)
    return (x,y)

def findDiffs(pt0, pt1):
    x = pt1[0]-pt0[0]
    y = pt1[1]-pt0[1]
    return (x,y)

def drawBorder(img, symbol, color, thickness):
    cv2.line(img, symbol[0], symbol[1], color, thickness)
    cv2.line(img, symbol[1], symbol[2], color, thickness)
    cv2.line(img, symbol[2], symbol[3], color, thickness)
    cv2.line(img, symbol[3], symbol[0], color, thickness)
            
def arenaReady():
    ready = True
    for corner in arenaCorners:
        if corner[0]==0 and corner[1]==0:
            ready = False
    return ready

def trackbarCallback(v):
    global dm_timeout, dm_read
    dm_timeout = v
    dm_read = DataMatrix(max_count = dm_max, timeout = dm_timeout, shape = DataMatrix.DmtxSymbol10x10)
    return

###############
## SETUP
###############

index_pattern = re.compile('^\d+$')
bot_pattern = re.compile('^(\d{2})$')
arena_pattern = re.compile('^C(\d)$')

cameraindex = 0
resolutionindex = 0
resolutions = [(640,480),(1280,720),(1920,1080)]

cv2.namedWindow("ArenaScanner")

cv2.startWindowThread()

key = -1

displayMode = 1

maxBots = 1

#Prompt for settings
#Camera ID
print str(sys.argv)
print "------------------------------"
if len(sys.argv) >= 2:
    in_str = sys.argv[1]
else:
    print "Enter the camera's index"
    in_str = raw_input("defaults [%1d] " % cameraindex)
match = index_pattern.match(in_str)
if match:
    print "using "+match.group(0)
    cameraindex = int(match.group(0))
else:
    print "using default"

#Resolution
if len(sys.argv) >= 3:
    in_str = sys.argv[2]
else:
    print "Enter the camera's resolution "
    for idx,(x,y) in enumerate(resolutions):
        print "[{}] {}x{}".format(idx,x,y)
    in_str = raw_input("defaults [%1d] " % resolutionindex)
match = index_pattern.match(in_str)
if match:
    print "using "+match.group(0)
    resolutionindex = int(match.group(0))
else:
    print "using default"

cap = cv2.VideoCapture(cameraindex)
cap.set(CV_CAP_PROP_FRAME_WIDTH, resolutions[resolutionindex][0])
cap.set(CV_CAP_PROP_FRAME_HEIGHT, resolutions[resolutionindex][1])

#DataMatrix  
dm_max = maxBots + 4; #four corners plus the bots
dm_timeout = 200
dm_read = DataMatrix(max_count = dm_max, timeout = dm_timeout, shape = DataMatrix.DmtxSymbol10x10)

#Trackbar
cv2.createTrackbar('Timeout','ArenaScanner',dm_timeout,1000, trackbarCallback)

colorCode = ((255,0,0), (0,240,0), (0,0,255), (29,227,245), (224,27,217)) #Blue, Green, Red, Yellow, Purple

arenaSize = (70.5, 46.5) #Arena size in inches

arenaCorners = [(0,0),(0,0),(0,0),(0,0)]
arenaInnerCorners = [(0,0),(0,0),(0,0),(0,0)]

botLocAbs = [(0,0), (0,0), (0,0), (0,0)]
botLocArena = [(0,0), (0,0), (0,0), (0,0)]
botHeading = [0, 0, 0, 0]
botAlive = [False, False, False, False]

gameOn = False

###############
## LOOP
###############
while True:
    #get next frame from capture device
    success, origImg = cap.read()
    if not success:
        print("Error reading from camera.");
        break;

    #Apply image transformationse
    modImg = cv2.cvtColor(origImg, cv2.COLOR_BGR2GRAY) #convert to grayscale
    width = size(modImg, 1)
    height = size(modImg, 0)
    if displayMode >= 2:
        outputImg = zeros((height,width,3), uint8) #create a blank image
    elif displayMode == 0:
        outputImg = cv2.cvtColor(modImg, cv2.COLOR_GRAY2BGR)        
    else:
        outputImg = origImg;

    #Scan for DataMatrix
    dm_read.decode(width, height, buffer(origImg.tostring()))
    #print dm_read.count()    

    #draw borders on detected symbols and record object locations
    for x in range(1, dm_read.count()+1):
        symbol = dm_read.stats(x)
        
        #Arena Corners
        match = arena_pattern.match(symbol[0])
        if match:
            c = int(match.group(1))
            if displayMode < 3:
                drawBorder(outputImg, symbol[1], colorCode[0], 2)
                pt = (symbol[1][1][0]-35, symbol[1][1][1]-25)  
                cv2.putText(outputImg, str(c), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[0], 2)
                arenaCorners[c] = symbol[1][c]
                ic = (c+2)%4
                arenaInnerCorners[c] = symbol[1][ic]

        #Bot Symbol
        match = bot_pattern.match(symbol[0])
        if match:
            pt = findCenter(symbol[1])
            botId = int(match.group(1))
            if botId >= maxBots:
                continue

            #update the bots location
            botLocAbs[botId] = pt
            if arenaReady():            
                wallCenterX = findDiffPt(arenaCorners[1],arenaCorners[0])
                wallCenterY = findDiffPt(arenaCorners[3],arenaCorners[0])
                maxX = arenaCorners[1][0]-arenaCorners[0][0]
                maxY = arenaCorners[3][1]-arenaCorners[0][1]
                arenaPtX = int(float(pt[0]-wallCenterY[0])/float(maxX)*arenaSize[0])
                arenaPtY = int(float(pt[1]-wallCenterX[1])/float(maxY)*arenaSize[1])
                botLocArena[botId] = (arenaPtX, arenaPtY)
                
            #update the bots heading
            x = symbol[1][3][0] - symbol[1][0][0]
            y = symbol[1][0][1] - symbol[1][3][1]
            h = math.degrees(math.atan2(y,x))
            if h < 0: h = 360 + h
            botHeading[botId] = int(round(h,0))

            #draw the borders, heading, and text for bot symbol
            if displayMode < 3:
                drawBorder(outputImg, symbol[1], colorCode[1], 2)                  
                pt = (pt[0]-15, pt[1]+10)            
                cv2.putText(outputImg, match.group(1), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[1], 2)
                ptdiff = findDiffs(symbol[1][1], symbol[1][2])
                pt0 = findDiffPt(symbol[1][2], symbol[1][3])
                pt1 = (pt0[0]+int(ptdiff[0]*1.20), pt0[1]+int(ptdiff[1]*1.20))
                cv2.line(outputImg, pt0, pt1, colorCode[1], 2)




    #Draw Objects
    #Arena
    drawBorder(outputImg, arenaCorners, colorCode[0], 2)  
    drawBorder(outputImg, arenaInnerCorners, colorCode[0], 1)  

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

    #Draw Statuses
    lh = 20 #line height
    pt = (0,40)
    for idx in range(0,4):
        if botLocAbs[idx][0]==0 and botLocAbs[idx][1]==0:
            continue
        status = str(idx)+":"+str(botLocArena[idx])+' '+str(botHeading[idx])
        cv2.putText(outputImg, status, pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[4], 2)
        pt = (pt[0],pt[1]+lh)
    
    #Game Status
    pt = (0,height-10)
    status = "Game On" if gameOn else "Game Off"
    cv2.putText(outputImg, status, pt, cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[4], 2)

    #crosshair in center
    pt0 = (width/2,height/2-5)
    pt1 = (width/2,height/2+5)
    cv2.line(outputImg, pt0, pt1, colorCode[4], 2)
    pt0 = (width/2-5,height/2)
    pt1 = (width/2+5,height/2)
    cv2.line(outputImg, pt0, pt1, colorCode[4], 2)
        
    #Display Mode       
    if displayMode == 0: #display source image
        outputImg = origImg
        displayModeLabel = "source"   
        
    elif displayMode == 1: #display source with data overlay
        displayModeLabel = "overlay"

    elif displayMode == 2: #display only data overlay
        displayModeLabel = "data"

    elif displayMode == 3: #display the only the bots point of view
        displayModeLabel = "bot"

    cv2.putText(outputImg, displayModeLabel, (0,15), cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[4], 2)
    cv2.putText(outputImg, "Bots:"+str(maxBots), (110,15), cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[4], 2)
    cv2.putText(outputImg, "timeout:"+str(dm_timeout), (220,15), cv2.FONT_HERSHEY_PLAIN, 1.5, colorCode[4], 2)
    cv2.imshow("ArenaScanner", outputImg)


    #Process key presses        
    key = cv2.waitKey(1) & 0xFF        
    if key == 27:  #esc
        break #exit
    
    
###############
## END LOOP
###############
cap.release()
cv2.destroyAllWindows()      
print
print "Exiting."
print    



