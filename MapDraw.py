#Daniel Liu
import pygame as p
import math as m
from MapGen import *


#Scale Variables
mapScale = 256

#Init calls
p.init()
MapGen.initGraphics(mapScale)

#Set up screen
tscreenX, tscreenY = 800,600
screenX, screenY = 200,150
screen = p.display.set_mode((tscreenX, tscreenY))
centerX, centerY = int(tscreenX/2), int(tscreenY/2)

#Create Objects
#Generate the map
map1 = MapGen(16,3.2)
map1.mrGenny()
map1.mrClassy()
map1.mrRoomy()
pprint(map1.layoutMap)

#Create clock
clock = p.time.Clock()


#Move function for testing
def move(cameraX,cameraY,speed,currentTimeDelta):
    POFFX, POFFY = 0, 0 #Camera direction variables
    
    #Determine direction of movement
    if p.key.get_pressed()[p.K_d]: #Right
        POFFX = 1
    if p.key.get_pressed()[p.K_w]: #Up
        POFFY = -1
    if p.key.get_pressed()[p.K_a]: #Left
        POFFX = -1
    if p.key.get_pressed()[p.K_s]: #Down
        POFFY = 1

    #Move camera position
    if (POFFX, POFFY) != (0, 0):
        angle = m.atan2(POFFY,POFFX)
        #Vary pixel per update depending on time it took for previous update
        cameraX += speed*currentTimeDelta*m.cos(angle) 
        cameraY += speed*currentTimeDelta*m.sin(angle)

    return cameraX, cameraY


#Set up camera
cspeed = 400
#Make camera start in middle of start room
for i in range(len(map1.level)):
    for n in range(len(map1.level[i])):
        if map1.level[i][n] == 5:
            cameraX, cameraY = n*mapScale+mapScale/2, i*mapScale+mapScale/2
            

#Active loop
running = True
while running:

    #Time stepping
    #Update timedelta to maintain constant movement in space and time
    timedelta = clock.tick(60)
    seconds = timedelta/1000  #Convert from milliseconds to seconds
    #Maintain range for deltatime
    if seconds > 50/1000:
        seconds = 50/1000
        
    click = False
    for evt in p.event.get():
        #quit
        if evt.type == p.QUIT:
            running = False

        #update mouse inputs
        pos1, pos2 = p.mouse.get_pos()
        m1, m2, m3 = p.mouse.get_pressed()

        #Determines if mouse is being clicked
        if evt.type == p.MOUSEBUTTONDOWN:
            click = True

    #Update screen
    screen.fill((47,40,58))
    
    #Move the camera
    cameraX,cameraY = move(cameraX,cameraY,cspeed,seconds)

    
    #Chunk loading
    #Determine which map elements are within seeing range of character
    #Find the levelMap coordinates of the top left most map element that can be seen
    TLRoomX, TLRoomY = int((cameraX-screenX/2)/mapScale), int((cameraY-screenY/2)/mapScale) #Top left corner of screen
    BRRoomX, BRRoomY = int((cameraX+screenX/2)/mapScale), int((cameraY+screenY/2)/mapScale) #Bot right corner of screen

    #Amount of map elements the camera can sees
    loadX, loadY = BRRoomX-TLRoomX+1, BRRoomY-TLRoomY+1

    #Draw the visible chunks
    for i in range(loadY):
        for n in range(loadX):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(map1.levelMap) and 0 <= TLRoomY+i < len(map1.levelMap):
                #Draw room
                scalepic = map1.levelMap[TLRoomY+i][TLRoomX+n][-1]
                screen.blit(scalepic, ((TLRoomX+n)*mapScale-cameraX+tscreenX/2, (TLRoomY+i)*mapScale-cameraY+tscreenY/2)) #Move map depending on camera location
                
                #Draw room layout
                if map1.layoutMap[TLRoomY+i][TLRoomX+n] != []:
                    scalepic = map1.layoutMap[TLRoomY+i][TLRoomX+n][-1]
                    screen.blit(scalepic, ((TLRoomX+n)*mapScale-cameraX+tscreenX/2, (TLRoomY+i)*mapScale-cameraY+tscreenY/2)) #Move map depending on camera location


    #Draw position marker
    p.draw.circle(screen, (0,255,0), (centerX, centerY), 4)
    p.draw.rect(screen, (0,0,255), (centerX-screenX/2, centerY-screenY/2, screenX, screenY), 1)
    p.display.flip()
    
p.quit()
