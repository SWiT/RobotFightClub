import cv2, cv

cap = cv2.VideoCapture(1)
cv2.namedWindow("ArenaScanner")
key = -1
while(key < 0):
    success, img = cap.read()

    imgGray = cv2.cvtColor(img, cv.CV_RGB2GRAY)
    features = cv2.goodFeaturesToTrack(imgGray, 300, 0.01, 10)
    drawcolors = ((255,0,0), (0,255,0), (0,0,255))
    i = 1
    drawcolor = drawcolors[i]
    
    for obj in features:
        for x,y in obj:
            i=i+1
            if i>=3:
                i=0
            drawcolor = drawcolors[i]
            
            x = int(x)
            y = int(y)
            cv2.circle(img, (x,y), 3, drawcolor, -1, 8, 0)
            #cv2.line(img, (x,y), (xprev,yprev), drawcolor)
            
  
    cv2.imshow("ArenaScanner", img)
    key = cv2.waitKey(1)
    

cap.release()
cv2.destroyAllWindows() 
