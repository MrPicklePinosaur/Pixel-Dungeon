from MapGen import *
import pygame as p
import math as m

scale = 128

screenX, screenY = 800,600
#Init
p.init()
MapGen.initGraphics()

#Generate the map
map1 = MapGen(16,3.2)
MapGen.mrGenny(map1)
map1.mrClassy()
pprint(map1.level)

#Initate graphics
screen = p.display.set_mode((screenX, screenY))

#Move function
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
            cameraX, cameraY = n*scale+scale/2, i*scale+scale/2
            


#Create clock
clock = p.time.Clock()

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

    screen.fill((255,0,0))

    #Move the camera
    cameraX,cameraY = move(cameraX,cameraY,cspeed,seconds)
    #Chunk loading
    #Determine which map elements are within seeing range of character
    #Find the levelMap coordinates of the top left most map element that can be seen
    TLRoomX, TLRoomY = round((cameraX-scale)/scale), round((cameraY-scale)/scale)

    #Draw the visible chunks (3x3)
    for i in range(3):
        for n in range(3):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(map1.levelMap) and 0 <= TLRoomY+i < len(map1.levelMap):
                scalepic = p.transform.scale(map1.levelMap[TLRoomY+i][TLRoomX+n][-1], (scale,scale))
                screen.blit(scalepic, ((TLRoomX+n)*scale-cameraX+screenX/2, (TLRoomY+i)*scale-cameraY+screenY/2)) #Move map depending on camera location
            else: #Otherwise, if the map element is not on levelMap, assume that it is an empty element
                scalepic = p.transform.scale(MapGen.otherDict['other'], (scale,scale))
                screen.blit(scalepic, ((TLRoomX+n)*scale-cameraX+screenX/2, (TLRoomY+i)*scale-cameraY+screenY/2))

    p.display.flip()
p.quit()
