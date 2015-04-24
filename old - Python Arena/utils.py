import cv2,math

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
    for idx,pt0 in enumerate(symbol):
        idx+=1
        if idx >= len(symbol): idx = 0
        pt1 = symbol[idx]
        cv2.line(img, pt0, pt1, color, thickness)
    return
