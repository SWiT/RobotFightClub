import time

class Bot:
    used_serialdev = []
    def __init__(self, idx):
        self.id = idx
        self.locZonePx = (0,0)
        self.locZone = (0,0)
        self.locArena = (0,0)
        self.heading = 0
        self.alive = False
        self.time = time.time()
        self.serialdev = None
        return
          
     
