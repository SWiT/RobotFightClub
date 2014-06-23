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
        
    def writeDM(self):
        # Write a Data Matrix barcode
        dm_write = DataMatrix()
        dm_write.encode("Hello, world!")
        dm_write.save("hello.png", "png")
        return
