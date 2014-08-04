import cv2, serial, time, os, re
from numpy import *
import arena,ui,dm
from utils import *
   
###############
## SETUP
###############
Arena = arena.Arena()
ui = ui.UI()

cv2.namedWindow("ArenaScanner")
cv2.namedWindow("ArenaControlPanel")
cv2.startWindowThread()

allImg = None

#DataMatrix  
#Do initial "deep" scan to find eveything.
dm = dm.DM((Arena.numbots + 4 + (Arena.numzones-1)*2), 100)
#dm = dm.DM(1, 100)

corner_pattern = re.compile('^C(\d)$')
bot_pattern = re.compile('^(\d{2})$')

cv2.createTrackbar('Scan (ms)', 'ArenaControlPanel', dm.timeout, 1000, dm.setTimeout)
cv2.createTrackbar('Threshold', 'ArenaControlPanel', Arena.threshold, 255, Arena.setThreshold)
cv2.setMouseCallback("ArenaControlPanel", ui.onMouse, (Arena,dm))

###############
## LOOP
###############
while True:
    
    for z in Arena.zone:
        #skip if capture is disabled
        if z.cap == -1:
            continue
            
        #get the next frame from the zones capture device
        success, origImg = z.cap.read()
        if not success:
            print("Error reading from camera: "+str(z.vdi));
            ui.exit = True
            break;
        width = size(origImg, 1)
        height = size(origImg, 0)

        #Apply image transformations
        threshImg = cv2.cvtColor(origImg, cv2.COLOR_BGR2GRAY) #convert to grayscale
        ret,threshImg = cv2.threshold(threshImg, Arena.threshold, 255, cv2.THRESH_BINARY)
        
        #Start Output Image
        if ui.isDisplayed(z.id):
            if ui.displayMode >= 2:
                outputImg = zeros((height, width, 3), uint8) #create a blank image
            elif ui.displayMode == 0:
                outputImg = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2BGR)
            else:
                outputImg = origImg;
            
        #Scan for DataMatrix
        dm.scan(origImg)

        #For each detected DataMatrix symbol
        for content,symbol in dm.symbols:
            #Zone Corners
            match = corner_pattern.match(content)
            if match:
                sval = int(match.group(1))
                for idx,corner in enumerate(z.corners):
                    if sval == corner.symbolvalue:
                        corner.locPx = symbol[idx]
                        corner.symbolcenter = findCenter(symbol)
                        
                        offset = int(corner.gap * (symbol[1][0]-symbol[0][0]) / corner.symboldimension)
                        offset_x_sign = 1 if (idx%3 != 0) else -1
                        offset_y_sign = 1 if (idx < 2) else -1
                        
                        corner.location = (corner.location[0] + offset_x_sign * offset, corner.location[1] + offset_y_sign * offset)
                        
                        corner.time = time.time()
                        if ui.isDisplayed(z.id) and ui.displayMode < 3:
                            drawBorder(outputImg, symbol, ui.COLOR_BLUE, 2)
                            pt = (symbol[1][0]-35, symbol[1][1]-25)  
                            cv2.putText(outputImg, str(sval), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, ui.COLOR_BLUE, 2)
            
            #Bot Symbol
            match = bot_pattern.match(content)
            if match:
                botId = int(match.group(1))
                if botId < 0 or Arena.numbots <=botId:
                    continue
                bot = Arena.bot[botId]
                bot.setData(symbol, z, threshImg)    #update the bot's data
                if ui.isDisplayed(z.id) and ui.displayMode < 3:
                    bot.drawOutput(outputImg)   #draw the bot's symbol

        
        #Draw Objects on Scanner window if this zone is displayed
        if ui.isDisplayed(z.id):
            #Crosshair in center
            pt0 = (width/2,height/2-5)
            pt1 = (width/2,height/2+5)
            cv2.line(outputImg, pt0, pt1, ui.COLOR_PURPLE, 1)
            pt0 = (width/2-5,height/2)
            pt1 = (width/2+5,height/2)
            cv2.line(outputImg, pt0, pt1, ui.COLOR_PURPLE, 1)
            
            #Zone edges
            corner_pts = []
            for corner in z.corners:
                #print corner.location
                corner_pts.append(corner.location)
            #print corner_pts
            drawBorder(outputImg, corner_pts, ui.COLOR_BLUE, 2)
            

            #Last Known Bot Locations
            for bot in Arena.bot:
                if bot.zid == z.id:                
                    bot.drawLastKnownLoc(outputImg)
        
        #Merge images if Display: All
        if ui.display == -1:
            if allImg is None or z.id == 0: #not set or first
                allImg = zeros((height, width*Arena.numzones, 3), uint8)
            #print z.id, height, width, Arena.numzones, size(outputImg,0), size(outputImg,1)
            if size(outputImg,0) == height and size(outputImg,1) == width:
                allImg[0:height, (z.id*width):((z.id+1)*width)] = outputImg
            if z.id+1 == len(Arena.zone):   #last
                outputImg = allImg
    
    #End of zone loop
    
    #Read from each bots serial device
    for bot in Arena.bot:                   
        if bot.sdi != -1:
            data = bot.serial.readline()            
            if data.strip() == "$W":
                reply = "{0:["
                #{0:[[x, y, heading, alive, botid, teamid],...]}
                for sbot in Arena.bot:
                    reply += "["
                    reply += str(sbot.locZone[0])
                    reply += ","+str(sbot.locZone[1])
                    reply += ","+str(sbot.heading)
                    reply += ","+str(sbot.alive)
                    reply += ","+str(sbot.id)
                    reply += ","+str(sbot.id)
                    reply += "]"
                reply += "]}\n"
                print reply.strip()
                bot.serial.write(reply)
            else:
                print "'"+data.strip()+"'"
            
    controlPanelImg = ui.drawControlPanel(Arena)

    outputImg = ui.resize(outputImg)

    #Display the image or frame of video
    cv2.imshow("ArenaScanner", outputImg)
    cv2.imshow("ArenaControlPanel", controlPanelImg)

    ui.calcFPS()

    #Exit
    if ui.exit: 
        break
      
###############
## END LOOP
###############
for z in Arena.zone:
    z.close()
cv2.destroyAllWindows()

print "Exiting."



