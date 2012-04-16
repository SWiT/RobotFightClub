import cv2
from numpy import *

def onMouse (event, x, y, flags, param):
    #print event, x, y, flags, param
    global objectsPts
    global objectPntIndex
    global nextPts
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
            #print objectsPts
            
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

##Setup Instructions
cap = cv2.VideoCapture(1)
cv2.namedWindow("ArenaScanner")
key = -1
nextPts = resetObjData()

drawing = True
tracking = False
drawObjects = True

dataview = 0

objectsColorCode = ((255,0,0), (0,240,0), (0,0,255), (0,210,210))
objectsColorName = ("Blue", "Green", "Red", "Yellow")
objectIndex = 0    #index of next object to add to
objectPntIndex = 0    #index of next point to add
objectsPts = resetAllData()

pointer = (0,0)

cv2.setMouseCallback("ArenaScanner", onMouse)
success, prevImg = cap.read()

displayMenu()
displayStatuses()

##Run Loop
while True:
        
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

    elif key == 104: #h key
        displayMenu()

    elif key == 112: #p key
        drawObjects = not drawObjects
        displayPrint("objectsPts:",objectsPts.shape)
        displayPrint(objectsPts)
        
    elif key == 114: #r key
        objectsPts[objectIndex] = resetObjData()
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
        displayPrint("Reset All")
    
    elif key > 0:
        displayPrint("unknown key",key)


    #get next frame from capture device
    success, nextImg = cap.read()


    #Apply image transformations
    if dataview == 0:
        outputImg = nextImg.copy()

    nextImg = cv2.cvtColor(nextImg, cv2.COLOR_BGR2GRAY)
    if dataview == 1:
        outputImg = nextImg.copy()

    nextImg = cv2.dilate(nextImg, None, iterations=1)
    if dataview == 2:
        outputImg = nextImg.copy()

    retval,nextImg = cv2.threshold(nextImg, 200, 255, cv2.THRESH_BINARY)
    if dataview == 3:
        outputImg = nextImg.copy()

        
    #Point Tracking and Detection
    if tracking:
        objIndex = 0
        for objPts in objectsPts:
            if len(objPts)>0:
                nextPts,status,err = cv2.calcOpticalFlowPyrLK(prevImg, nextImg, objPts, nextPts)
            objectsPts[objIndex] = nextPts.copy()
            objIndex += 1

            
    #Draw points on output
    if drawObjects:
        objIndex = 0
        s = objectsPts.shape
        li = s[1]-1 #last index
        for objPts in objectsPts:
            px,py = 0,0
            for x,y in objPts:    
                x,y = int(x),int(y)
                if x>0 or y>0:
                    cv2.circle(outputImg, (x,y), 3, objectsColorCode[objIndex], -1, 8, 0)
                    if px>0 or py>0:
                        cv2.line(outputImg, (px,py), (x,y), objectsColorCode[objIndex], 1)
                    elif (objPts[li][0]>0 or objPts[li][1]>0):
                        px,py = objPts[li]
                        cv2.line(outputImg, (px,py), (x,y), objectsColorCode[objIndex], 1)
                    px,py = x,y
                   
            objIndex+=1
        
    if drawing:
        cv2.circle(outputImg, pointer, 4, objectsColorCode[objectIndex], -1, 8, 0)
        
    #Draw output        
    cv2.imshow("ArenaScanner", outputImg)

    prevImg = nextImg.copy()

print "Exiting."    

cap.release()
cv2.destroyAllWindows() 
