import sys, math
import itertools
import cv

def detectFeatures(img):
  """Detect features.
  \param img Grayscale input image.
  \return Feature iterator.
  """
  eig_image = cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_32F, 1)
  temp_image = cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_32F, 1)
  return cv.GoodFeaturesToTrack(img, eig_image, temp_image, 150, 0.01, 10, None, 3, 0, 0.04)

def distance(p0, p1):
  return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
  
def groupPoints(pointList, minDistance):
  pointGroups = []
  for point in pointList:
    done = False # done grouping this point?
    for pointGroup in pointGroups:
      for point2 in pointGroup:
        if done == False:
          if distance(point, point2) < minDistance:
            pointGroup.append(point)
            done = True
    if done == False: # didn't find a good group
      newGroup = [point]
      pointGroups.append(newGroup)
  return pointGroups


cv.NamedWindow("ArenaScannerOrg", 1)
cv.NamedWindow("ArenaScanner", 2)
capture = cv.CaptureFromCAM(0)
while True:
    img = cv.QueryFrame(capture)
    image_size = cv.GetSize(img)
    
##    imgoutput = cv.CreateImage(image_size, 8, 1)
##    cv.CvtColor(img, imgoutput, cv.CV_RGB2GRAY)

##    imgoutput = cv.CloneImage(img);
##    hc = cv.Load("C:\opencv\data\haarcascades\haarcascade_frontalface_default.xml")
##    faces = cv.HaarDetectObjects(img, hc, cv.CreateMemStorage())
##    for (x,y,w,h),n in faces:
##        cv.Rectangle(imgoutput, (x,y), (x+w,y+h), 255)


##    imghsv = cv.CreateImage(image_size, 8, 3)
##    cv.CvtColor(img, imghsv, cv.CV_BGR2HSV)
##    imgoutput = cv.CreateImage(image_size, 8, 1)
##    cv.InRangeS(imghsv, cv.Scalar(20, 100, 100), cv.Scalar(30, 255, 255), imgoutput) #yellow

    imgoutput = cv.CloneImage(img)
    imgGrey = cv.CreateImage(image_size, 8, 1)
    cv.CvtColor(img, imgGrey, cv.CV_RGB2GRAY)
    imgGreySm = cv.CreateImage(cv.GetSize(imgGrey), imgGrey.depth, 1)
    cv.Smooth(imgGrey, imgGreySm, smoothtype=cv.CV_MEDIAN, param1=9)
    
    features = detectFeatures(imgGreySm)
    featureList = list(features)
    for (x,y) in featureList:
      cv.Circle(imgoutput, (int(x),int(y)), 3, (0,255,0), -1, 8, 0)


    # detect objects
    minDistance = 50
    featureGroups = groupPoints(featureList, minDistance)
    for group in featureGroups:
      print group
      for i in range(len(group) - 1):
        cv.Line(imgoutput, (int(group[i][0]), int(group[i][1])), (int(group[i+1][0]), int(group[i+1][1])), (0,0,255))
  



    
    cv.ShowImage("ArenaScannerOrg", img)
    cv.ShowImage("ArenaScanner", imgoutput)
    if cv.WaitKey(10) == 27:  #esc key
        break
    
cv.DestroyWindow("ArenaScannerOrg")
cv.DestroyWindow("ArenaScanner")
