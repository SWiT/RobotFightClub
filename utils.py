import cv2,math
from numpy import *
from pydmtx import DataMatrix

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
    cv2.line(img, symbol[0], symbol[1], color, thickness)
    cv2.line(img, symbol[1], symbol[2], color, thickness)
    cv2.line(img, symbol[2], symbol[3], color, thickness)
    cv2.line(img, symbol[3], symbol[0], color, thickness)
    
class DM:
    def __init__(self, max_count, timeout):
        self.max_count = max_count
        self.timeout = timeout
        self.loadReader()
        self.symbols = []   #a symbol is a list of the content and four (x,y) points as a sub list
        return
        
    def loadReader(self):
        self.read = DataMatrix(max_count = self.max_count, timeout = self.timeout, shape = DataMatrix.DmtxSymbol10x10)
        return
            
    def scan(self, img):
        self.read.decode(size(img, 1), size(img, 0), buffer(img.tostring()))
        self.symbols = []
        for idx in range(1, self.read.count()+1):
            self.symbols.append(self.read.stats(idx))
        
    def setTimeout(self, v):
        self.timeout = v
        self.loadReader()
        return
        
    def setMaxCount(self, v):
        self.max_count = v
        self.loadReader()
        return
        

