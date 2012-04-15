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
        if drawing:
            pointer = (x, y)


def resetAllData ():
    data = array([
                [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
                ,[(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
                ,[(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
                ,[(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
                ], dtype=float32)
    return data


def resetObjData ():
    data = array([(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)], dtype=float32)
    return data


def displayMenu ():
    print ""
    print "------------------------------"
    print "'c' Change color of next point "
    print "'d' Toggle drawing points."
    print "'h' Print this help menu."
    print "'p' Print Points"
    print "'r' Reset all points for current color"
    print "'s' Print Statuses"
    print "'t' Start tracking"
    print "'Esc' or 'Space bar' to exit."
    print "------------------------------"

def displayStatuses ():
    print ""
    print "------------------------------"
    print "Drawing: ",drawing
    print "Color: "+objectsColorName[objectIndex]
    print "Tracking: ",tracking
    print "------------------------------"

def displayPts ():
    print ""
    print "------------------------------"
    print "pointer:", pointer
    print "objectsPts:", objectsPts
    print "------------------------------"

##Setup Instructions
cap = cv2.VideoCapture(1)
cv2.namedWindow("ArenaScanner")
key = -1
nextPts = array([], dtype=float32)

drawing = True
tracking = False

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
    success, nextImg = cap.read()
    outputImg = nextImg.copy()
    
    #process key presses        
    key = cv2.waitKey(1)        
    if key == 27 or key == 32:  #esc or spacebar
        break #exit
    elif key == 104: #h key
        displayMenu()
        
    elif key == 115: #s key
        displayStatuses()

    elif key == 112: #p key
        displayPts();
        
    elif key == 99: #c key
        objectIndex += 1
        if objectIndex >= len(objectsColorCode):
            objectIndex = 0
        objectPntIndex = 0
        print ""
        print "------------------------------"
        print "Color: "+objectsColorName[objectIndex]
        print "------------------------------"

    elif key == 100: #d key
        drawing = not drawing
        if drawing:
            tracking = False
        displayStatuses()
        
    elif key == 114: #r key
        objectsPts[objectIndex] = resetObjData()
        print ""
        print "------------------------------"
        print "Reset: "+objectsColorName[objectIndex]
        print "------------------------------"
        
    elif key == 120: #x key
        objectsPts = resetAllData()
        print ""
        print "------------------------------"
        print "Reset All"
        print "------------------------------"

    elif key == 116: #t key
        tracking = not tracking
        if tracking:
            drawing = False
        displayStatuses()
        
    elif key > 0:
        print ""
        print "------------------------------"
        print "unknown key "+str(key)
        print "------------------------------"


    #Point Tracking and Detection
    if tracking:
        objIndex = 0
        for objPts in objectsPts:
            if len(objPts)>0:
                nextPts,status,err = cv2.calcOpticalFlowPyrLK(prevImg, nextImg, objPts, nextPts)
            objectsPts[objIndex] = nextPts.copy()
            objIndex += 1

            
    #Draw points on output
    objIndex = 0
    for objPts in objectsPts:
        px = 0
        py = 0
        i = 0
        s = objectsPts.shape
        li = (s[1]-1) #last index
        for x,y in objPts:    
            x = int(x)
            y = int(y)
            if x>0 or y>0:
                cv2.circle(outputImg, (x,y), 3, objectsColorCode[objIndex], -1, 8, 0)
                if px>0 or py>0:
                    cv2.line(outputImg, (px,py), (x,y), objectsColorCode[objIndex], 1)
                elif (objPts[li][0]>0 or objPts[li][1]>0):
                    px = objPts[li][0]
                    py = objPts[li][1]
                    cv2.line(outputImg, (px,py), (x,y), objectsColorCode[objIndex], 1)
                px = x
                py = y
            i += 1
        objIndex+=1
        
    if drawing:
        cv2.circle(outputImg, pointer, 4, objectsColorCode[objectIndex], -1, 8, 0)
        
    #Draw output        
    cv2.imshow("ArenaScanner", outputImg)

    prevImg = nextImg.copy()

print "Exiting."    

cap.release()
cv2.destroyAllWindows() 
