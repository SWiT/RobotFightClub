import cv2, cv
from numpy import *

cap = cv2.VideoCapture(1)
cv2.namedWindow("ArenaScanner")
key = -1
prevPts = array([])
nextPts = array([])
success, prevImg = cap.read()


drawcolors = ((255,0,0), (0,255,0), (0,0,255))
i = 0
outputgray = False
printPts = False

detectionModes = (["Off", "goodFeaturesToTrack"])
dm = 0

print "'Esc' to exit."
print "'g' to toggle grayscaled output."
print "'d' to change point detection mode."
print "'p' to output points"

while True:
    success, nextImg = cap.read()

    grayImg = cv2.cvtColor(nextImg, cv.CV_RGB2GRAY)

    #process key presses        
    key = cv2.waitKey(1)        
    if key == 27:  #esc key
        break
    
    elif key == 100: #d key
        dm += 1
        if dm >= len(detectionModes):
            dm = 0
        print "Point Detection "+detectionModes[dm]
        
    elif key == 103: #g key
        outputgray = not outputgray
        print "Grayscale "+str(outputgray)
        
    elif key == 112: #p key
        printPts = not printPts
        print "Output Points "+str(printPts)
        
    elif key > 0:
        print "unknown key "+str(key)


    #Set output to Grayscale or Color
    if outputgray:
        outputImg = grayImg
    else:
        outputImg = nextImg
        

    #Point Detetcion Mode
    if detectionModes[dm]=="goodFeaturesToTrack":
        nextPts = cv2.goodFeaturesToTrack(grayImg, 300, 0.01, 10)
    elif detectionModes[dm]=="Off":
        nextPts = array([])


    #Output Points
    if printPts:
        print nextPts


    #Draw points on output
    drawcolor = drawcolors[i]
    i+=1
    if i>=3:
        i=0
    for obj in nextPts:
        for x,y in obj:    
            x = int(x)
            y = int(y)
            cv2.circle(outputImg, (x,y), 3, drawcolor, -1, 8, 0)

    #Draw output        
    cv2.imshow("ArenaScanner", outputImg)

    prevPts = nextPts
    prevImg = nextImg

print "Exiting."    

cap.release()
cv2.destroyAllWindows() 
