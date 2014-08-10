import cv2
from numpy import *
import arena

   
###############
## SETUP
###############
Arena = arena.Arena()

cv2.namedWindow("ArenaScanner")
cv2.namedWindow("ArenaControlPanel")
cv2.startWindowThread()

cv2.createTrackbar('Scan (ms)', 'ArenaControlPanel', Arena.dm.timeout, 1000, Arena.dm.setTimeout)
#cv2.createTrackbar('Threshold1', 'ArenaControlPanel', Arena.zone[0].threshold, 255, Arena.zone[0].setThreshold)
cv2.setMouseCallback("ArenaControlPanel", Arena.ui.onMouse, Arena)

###############
## LOOP
###############
while True:
    Arena.deepScan()
    outputImg = Arena.render() 
    
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
            
    controlPanelImg = Arena.ui.drawControlPanel(Arena)

    #Display the image or frame of video
    if size(outputImg,0) > 0 and size(outputImg,1) > 0:
        outputImg = Arena.ui.resize(outputImg)
        cv2.imshow("ArenaScanner", outputImg)
    
    cv2.imshow("ArenaControlPanel", controlPanelImg)

    Arena.ui.calcFPS()

    #Exit
    if Arena.ui.exit: 
        break
      
###############
## END LOOP
###############
for z in Arena.zone:
    z.close()
cv2.destroyAllWindows()

print "Exiting."



