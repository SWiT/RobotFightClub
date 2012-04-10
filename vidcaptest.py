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
drawPts = False

print "'Esc' to exit."
print "'g' to toggle grayscaled output."

while True:
    success, nextImg = cap.read()

    grayImg = cv2.cvtColor(nextImg, cv.CV_RGB2GRAY)

    #process key presses        
    key = cv2.waitKey(1)        
    if key == 27:  #esc key
        break
    elif key == 103: #g key
        print "Grayscale "+str(outputgray)
        outputgray = not outputgray
    elif key == 112: #p key
        print "Draw Points "+str(drawPts)
        drawPts = not drawPts
    elif key > 0:
        print "unknown key "+str(key)

    #Set output to Grayscale or Color
    if outputgray:
        outputImg = grayImg
    else:
        outputImg = nextImg

    #Draw detected points on the output image
    if drawPts:
        nextPts = cv2.goodFeaturesToTrack(grayImg, 300, 0.01, 10)
        drawcolor = drawcolors[i]
        i=i+1
        if i>=3:
            i=0
        
        for obj in nextPts:
            for x,y in obj:    
                x = int(x)
                y = int(y)
                cv2.circle(outputImg, (x,y), 3, drawcolor, -1, 8, 0)

        
    
    cv2.imshow("ArenaScanner", outputImg)

    prevPts = nextPts
    prevImg = nextImg

    

cap.release()
cv2.destroyAllWindows() 
