import cv2
import sys, math
from numpy import *

###############
## FUNCTIONS
###############

def onMouse (event, x, y, flags, param):
    #print event, x, y, flags, param
    global objectsPts
    global objectPntIndex
    global outputImg
    global pointer
    
    if event == cv2.EVENT_LBUTTONUP:
        #print "LBUTTONUP", x, y, flags, param
        if drawing:
            s = objectsPts.shape
            objectsPts.itemset((objectIndex,objectPntIndex,0), x)
            objectsPts.itemset((objectIndex,objectPntIndex,1), y)
            objectPntIndex += 1
            if objectPntIndex >= s[1]:
                objectPntIndex = 0
            print "Added Point:",objectIndex,objectPntIndex,x,y
            
    if event == cv2.EVENT_MOUSEMOVE:
        pointer = (x, y)


def resetAllData ():
    data = array([
                [(0,0),(0,0),(0,0)]
                ,[(0,0),(0,0),(0,0)]
                ,[(0,0),(0,0),(0,0)]
                ,[(0,0),(0,0),(0,0)]
                ], dtype=float32)
    return data


def resetObjData ():
    data = array([(0,0),(0,0),(0,0)], dtype=float32)
    return data


def displayMenu ():
    print ""
    print "------------------------------"
    print "'c' Change color of next point "
    print "'d' Toggle adding points."
    print "'h' Print this help menu."
    print "'p' Print Points,toggle drawing of points"
    print "'r' Remove the current color points."
    print "'s' Print Statuses"
    print "'t' Start tracking"
    print "'v' Toggle output davta view."
    print "'x' Reset all points."
    print "'Esc' or 'Space bar' to exit."
    print "------------------------------"


def displayStatuses ():
    print ""
    print "------------------------------"
    print "Drawing:",drawing
    print "Color:",objectsColorName[objectIndex]
    print "Tracking:",tracking
    print "------------------------------"


def displayPrint(a, b=""):
    print ""
    print "------------------------------"
    print a, b
    print "------------------------------"


def drawObject(objPts, colorCode):
    px,py = 0,0
    li = objPts.shape[0]-1
    sz = 2
    for x,y in objPts:    
        x,y = int(x),int(y)
        if x>0 or y>0:
            cv2.circle(outputImg, (x,y), sz, colorCode, -1, 8, 0)
            if px>0 or py>0:
                cv2.line(outputImg, (px,py), (x,y), colorCode, 1)
            elif (objPts[li][0]>0 or objPts[li][1]>0):
                px,py = objPts[li]
                cv2.line(outputImg, (px,py), (x,y), colorCode, 1)
                
            if sz>2:
                sz = 2
            px,py = x,y

            
def dist(p0, p1):
  return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


def findCenterOfBlob(prevPt, color):
    nextPt = prevPt
    passes = 0
    while passes < 3:
        px,py = prevPt
        while Img[py][px] == color:
            py += 1 #down
            if py >= imgshape[0]:
                break
        max_y = py-1

        px,py = prevPt
        while  Img[py][px] == color:
            py -= 1 #up
            if py < 0:
                break
        min_y = py+1
        
        px,py = prevPt
        while  Img[py][px] == color:
            px += 1 #right
            if px >= imgshape[1]:
                break
        max_x = px-1

        px,py = prevPt
        while  Img[py][px] == color:
            px -= 1 #left
            if px < 0:
                break
        min_x = px+1

        nextPt[0] = min_x + (max_x-min_x)/2
        nextPt[1] = min_y + (max_y-min_y)/2

        if nextPt==prevPt:
            break
        passes+=1
        
    return nextPt


def findBots(Img):
    y=0
    for row in Img:
        x=0
        for pixel in row:
            if pixel==color:
                print "found",color,"at",x,",",y
                #cenPnt = findCenterOfBlob((x,y),255)
            x+=1
        y+=1




            
###############
## SETUP
###############            
if len(sys.argv) > 1:
  cap = cv2.VideoCapture(sys.argv[1])
else:
  cap = cv2.VideoCapture(0)
cv2.namedWindow("ArenaScanner")
key = -1

drawing = True
tracking = False
drawObjects = True

dataview = 3

objectsColorCode = ((255,0,0), (0,240,0), (0,0,255), (0,210,210))
objectsColorName = ("Blue", "Green", "Red", "Yellow")
objectIndex = 0    #index of next object to add to
objectPntIndex = 0    #index of next point to add
objectsPts = resetAllData()
objectsNextPts = resetAllData()

pointer = (0,0)

cv2.setMouseCallback("ArenaScanner", onMouse)
success, prevImg = cap.read()

displayMenu()
displayStatuses()


###############
## LOOP
###############
while True:
    #get next frame from capture device
    success, nextImg = cap.read()
    if not success:
        break;


    #Apply image transformations
    if dataview == 0:
        outputImg = nextImg.copy()

    nextImg = cv2.cvtColor(nextImg, cv2.COLOR_BGR2GRAY)
    if dataview == 1:
        outputImg = nextImg.copy()

    nextImg = cv2.dilate(nextImg, None, iterations=1)
    if dataview == 2:
        outputImg = nextImg.copy()

    retval,nextImg = cv2.threshold(nextImg, 170, 255, cv2.THRESH_BINARY)
    if dataview == 3:
        outputImg = nextImg.copy()
        

   
    #Point Tracking and Detection
    if tracking:
        prevPts = float32(objectsPts.reshape((12,2)))
        nextPts = zeros((12,2),dtype=float32)
        nextPts,status,err = cv2.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, nextPts)
        objectsNextPts = int32(nextPts.reshape((4,3,2)))
        objectsPts = objectsNextPts.copy()
            
            
    #Draw points on output
    if drawObjects:
        objIndex = 0
        for objPts in objectsPts:
            drawObject(objPts, objectsColorCode[objIndex])
            objIndex+=1
        
    if drawing:
        cv2.circle(outputImg, pointer, 2, objectsColorCode[objectIndex], -1, 8, 0)

        
    #Draw output        
    cv2.imshow("ArenaScanner", outputImg)

    
    #process key presses        
    key = cv2.waitKey(1)        
    if key == 27 or key == 32:  #esc or spacebar
        break #exit
        
    elif key == 99: #c key
        objectIndex += 1
        if objectIndex >= len(objectsColorCode):
            objectIndex = 0
        objectPntIndex = 0
        displayPrint("Color:",objectsColorName[objectIndex])

    elif key == 100: #d key
        drawing = not drawing
        displayStatuses()

    elif key == 102: #f key
        findBots(nextImg)
        
    elif key == 104: #h key
        displayMenu()

    elif key == 112: #p key
        drawObjects = not drawObjects
        displayPrint("objectsPts:",objectsPts.shape)
        displayPrint(objectsPts)
        
    elif key == 114: #r key
        objectsPts[objectIndex] = resetObjData()
        objectPntIndex = 0
        displayPrint("Reset:",objectsColorName[objectIndex])
    
    elif key == 115: #s key
        displayStatuses()

    elif key == 116: #t key
        tracking = not tracking
        displayStatuses()

    elif key == 118: #v key
        dataview += 1
        if dataview > 3:
            dataview = 0
        displayPrint("Data View:",dataview)

    elif key == 120: #x key
        objectsPts = resetAllData()
        objectPntIndex = 0
        displayPrint("Reset All")
    
    elif key > 0:
        displayPrint("unknown key",key)

    prevImg = nextImg.copy()
print "Exiting."    

cap.release()
cv2.destroyAllWindows()
