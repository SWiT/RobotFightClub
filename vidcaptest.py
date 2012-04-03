import cv2, cv

cap = cv2.VideoCapture(1)
cv2.namedWindow("ArenaScanner")
key = -1
while(key < 0):
    success, img = cap.read()

    imgGray = cv2.cvtColor(img, cv.CV_RGB2GRAY)
    features = cv2.goodFeaturesToTrack(imgGray, 100, 0.01, 10)
    dotcolors = ((255,0,0),(0,255,0),(0,0,255))
    i=0
    xprev = 0
    yprev = 0
    for obj in features:
        dotcolor = dotcolors[i]
        i=i+1
        if i>=3:
            i=0    
        for x,y in obj:            
            cv2.circle(img, (int(x),int(y)), 3, dotcolor, -1, 8, 0)
            cv2.line(img, (int(x), int(y)), (int(xprev), int(yprev)), dotcolor)
            xprev = x
            yprev = y
  
    cv2.imshow("ArenaScanner", img)
    key = cv2.waitKey(1)
    

cap.release()
cv2.destroyAllWindows() 
