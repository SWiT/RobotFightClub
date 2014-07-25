import cv2, time, subprocess
        
class Zone:
    used_vdi = []
    def __init__(self, idx, nzones, npoi, videodevices):
        self.id = idx
        self.vdi = idx
        self.videodevices = videodevices
        self.actualsize = (70.5, 46.5) #zone size in inches
        self.poisymbol = [-1,-1,-1,-1]
        self.poitime = [time.time(), time.time(), time.time(), time.time()] 
        self.xoffset = 0
        self.yoffset = 0 
        self.v4l2ucp = -1
        self.cap = -1        #capture device object (OpenCV)
        self.resolutions = [(640,480),(1280,720),(1920,1080)]
        self.ri = 1          #selected Resolution Index
        
        x = self.resolutions[self.ri][0]
        y = self.resolutions[self.ri][1]
        self.poi = [(0,y),(x,y),(x,0),(0,0)]

        self.poisymbol[0] = idx
        self.poisymbol[1] = idx + 1
        self.poisymbol[2] = npoi - idx - 2
        self.poisymbol[3] = npoi - idx - 1
        self.initVideoDevice()
        return
    
    def nextAvailableDevice(self):
        self.vdi += 1
        if self.vdi >= len(self.videodevices):
            self.vdi = -1
        if self.vdi != -1:
            try:
                self.used_vdi.index(self.vdi)
            except ValueError:
                return
            self.nextAvailableDevice()
        return
        
    def updateVideoDevice(self):
        self.close()
        self.nextAvailableDevice()
        if self.vdi != -1:
            self.initVideoDevice()
        else:
            self.close()    
        return
        
    def openV4l2ucp(self):
        self.v4l2ucp = subprocess.Popen(['v4l2ucp',self.videodevices[self.vdi]])
        return

    def closeV4l2ucp(self):
        if self.v4l2ucp != -1:
            self.v4l2ucp.kill()
            self.v4l2ucp = -1
        return
             
    def initVideoDevice(self):
        if self.vdi != -1:
            self.cap = cv2.VideoCapture(self.vdi)
            self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.resolutions[self.ri][0])
            self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.resolutions[self.ri][1])
            self.used_vdi.append(self.vdi)          
        return
        
    def close(self):
        self.closeV4l2ucp()
        self.closeCap()
        try:
            self.used_vdi.remove(self.vdi)
        except ValueError:
            pass
        return
    
    def closeCap(self):
        if self.cap != -1: 
            self.cap.release()
            self.cap = -1
        return
        
    def updateResolution(self):
        self.ri += 1
        if self.ri >= len(self.resolutions):
            self.ri = 0
        x = self.resolutions[self.ri][0]
        y = self.resolutions[self.ri][1]
        self.close()
        self.initVideoDevice()
        self.poi = [(0,y),(x,y),(x,0),(0,0)]
        return
