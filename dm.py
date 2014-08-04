from numpy import size
from pydmtx import DataMatrix
from PIL import Image
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
            
    def scan(self, img, offsetx = 0, offsety = 0):
        #print self.max_count, self.timeout
        self.read.decode(size(img, 1), size(img, 0), buffer(img.tostring()))
        self.symbols = []
        for idx in range(1, self.read.count()+1):
            data = list(self.read.stats(idx))
            data[1] = list(data[1])
            data[1][0] = (data[1][0][0] + offsetx, data[1][0][1] + offsety)
            data[1][1] = (data[1][1][0] + offsetx, data[1][1][1] + offsety)
            data[1][2] = (data[1][2][0] + offsetx, data[1][2][1] + offsety)
            data[1][3] = (data[1][3][0] + offsetx, data[1][3][1] + offsety)
            self.symbols.append(data)
        
    def setTimeout(self, v):
        self.timeout = v
        self.loadReader()
        return
        
    def setMaxCount(self, v):
        self.max_count = v
        self.loadReader()
        return
        
    def writeDM(self):
        # Write a Data Matrix barcode
        dm_write = DataMatrix()
        dm_write.encode("Hello, world!")
        dm_write.save("hello.png", "png")
        return
