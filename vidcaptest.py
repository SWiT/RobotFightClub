import cv2
from numpy import *

cap = cv2.VideoCapture(1)
cv2.namedWindow("ArenaScanner")
key = -1
prevPts = array([])
nextPts = array([])
success, prevImg = cap.read()

outputgray = False
printPts = False
blurInput = False

detectionModes = (["Off","goodFeaturesToTrack","calcOpticalFlowPyrLK","clickDefinedPoints"])
dm = 0

drawColors = ((255,0,0), (0,255,0), (0,0,255))
dc = 0


print "'Esc' to exit."
print "'g' to toggle grayscaled output."
print "'d' to change point detection mode."
print "'p' to output points"
print "'c' to change color"
print "'b' to blur input"


def onMouse (event, x, y, flags, param):
    global prevPts
    global nextPts
    if event == cv2.EVENT_LBUTTONUP:
##        print "LBUTTONUP", event, x, y, flags, param
        s = prevPts.shape
        ni = s[0]
        ns = ni + 1
        prevPts.resize((ns,1,2))
        prevPts.itemset((ni,0,0), x)
        prevPts.itemset((ni,0,1), y)
        nextPts = prevPts.copy()
        print nextPts
    
cv2.setMouseCallback("ArenaScanner", onMouse, nextPts)

while True:
    success, nextImg = cap.read()

    grayImg = cv2.cvtColor(nextImg, cv2.COLOR_RGBA2GRAY)

    #process key presses        
    key = cv2.waitKey(1)        
    if key == 27 or key == 32:  #esc or spacebar
        break #exit
    
    elif key == 98: #b key
        blurInput = not blurInput
        print "Blur Input "+str(blurInput)

    elif key == 99: #c key
        dc += 1
        if dc >= len(drawColors):
            dc = 0
        print "Change Color"

    elif key == 100: #d key
        dm += 1
        if dm >= len(detectionModes):
            dm = 0
        prevPts = array([])
        nextPts = array([])
        print "Point Detection "+detectionModes[dm]
        
    elif key == 103: #g key
        outputgray = not outputgray
        print "Grayscale "+str(outputgray)
        
    elif key == 112: #p key
        printPts = not printPts
        print "Output Points "+str(printPts)
        
    elif key > 0:
        print "unknown key "+str(key)

        
    if blurInput:
        grayImg = cv2.blur(grayImg, (5,5))
        nextImg = cv2.blur(nextImg, (5,5))

    #Set output to Grayscale or Color
    if outputgray:
        outputImg = copy(grayImg)
    else:
        outputImg = copy(nextImg)

    #Point Detection Mode
    if detectionModes[dm]=="Off":
        nextPts = array([])
    elif detectionModes[dm]=="goodFeaturesToTrack":
        nextPts = cv2.goodFeaturesToTrack(grayImg, 3, 0.01, 10)  
    elif detectionModes[dm]=="calcOpticalFlowPyrLK":
        if len(nextPts)==0:
            nextPts = cv2.goodFeaturesToTrack(grayImg, 3, 0.01, 10)
            prevPts = nextPts.copy()
        nextPts,status,err = cv2.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, nextPts)
    elif detectionModes[dm]=="clickDefinedPoints":
        if len(prevPts)>0 and len(nextPts)>0:
            print "prev",prevPts
            print "next",nextPts
            nextPts,status,err = cv2.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, nextPts)
            
    #Output Points
    if printPts:
        print nextPts

    #Draw points on output
    for obj in nextPts:
        for x,y in obj:    
            x = int(x)
            y = int(y)
            cv2.circle(outputImg, (x,y), 3, drawColors[dc], -1, 8, 0)
        
    #Draw output        
    cv2.imshow("ArenaScanner", outputImg)

    prevPts = nextPts.copy()
    prevImg = nextImg.copy()

print "Exiting."    

cap.release()
cv2.destroyAllWindows() 
