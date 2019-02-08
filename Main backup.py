#Daniel Liu

#Import Modules
import pygame as p
import math as m
import random as r
import Setup
from pprint import *
from Collider import *
from Entity import *
from MapGen import *
from Pathfinding import *
from Projectile import *
from Weapon import *

#Scale Variables
scale = Setup.scale
mapScale = Setup.mapScale
playerScale = Setup.playerScale

#Init calls
p.init()
MapGen.initGraphics(mapScale) #Load map images

#Set up screen
screenX, screenY = Setup.screenX, Setup.screenY
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = Setup.centerX, Setup.centerY
#Set up window
p.display.set_icon(p.image.load('assets/ui/logo.png'))
p.display.set_caption("Dungeon")


#Object Setups =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#Create Map
numOfElements = 16 
map1 = MapGen(numOfElements,3.2) #Create level map
map1.mrGenny() #Generate the room layout
map1.mrClassy() #Determine the type of room depending on the amount of exits has
map1.mrRoomy() #Generate the room layout of each room
map1.mrCollidey() #Merge the collsion data of the room and room layout
map1.mrDoory(scale) #Create all the doors

#Make a 2d array with all the collision data of all the rooms
for i in range(len(map1.level)): #Iterate through each room of map
    for n in range(len(map1.level[i])):
        rawMapCollide = Collider.importCollisionMap(n,i,numOfElements,map1.roomCollide[i][n],scale) #Create actual rect collision objects
        mapCollide = Collider.convertCollisionGrid(n,i,rawMapCollide,scale,numOfElements)
        map1.mrCollisionData[i][n] = mapCollide
        
pprint(map1.level)


#Players
#Load spritesheets
martialArtistSprite = p.transform.scale(p.image.load('assets/entities/martialArtist_spritesheet.png'), (5*playerScale, 2*playerScale))
knightSprite = knightSprite = p.transform.scale(p.image.load('assets/entities/templeKnight_spritesheet.png'), (5*playerScale, 2*playerScale))
#Create players
#Determine the coords of the center of the spawn room
for i in range(len(map1.level)):
    for n in range(len(map1.level[i])):
        if map1.level[i][n] == 5:
            spawnroomX, spawnroomY = n*mapScale+mapScale/2, i*mapScale+mapScale/2
            
px, py = spawnroomX, spawnroomY #player starting coords (should be in the center of the spawn room)

martialArtist = Player(martialArtistSprite,playerScale,playerScale,(20,35,10,10),100,300,px,py)
knight = Player(knightSprite,playerScale,playerScale,(0,0,playerScale,playerScale),120,250,px,py)

#Crop player sprites
martialArtist.spritesheetCrop(2,5)
knight.spritesheetCrop(2,5)

#Variables
curPlayer = martialArtist
count = 0


#Weapons
#Create new weapons with stats from stats file
#Projecitles
projectileData = XLSX.load('assets/data/weaponStats.xlsx','projectile')
projectileObjects = XLSX.createObjects(Projectile,projectileData)
#Melee weapons
meleeData = XLSX.load('assets/data/weaponStats.xlsx','melee')
meleeObjects = XLSX.createObjects(MeleeWeapon,meleeData)
#Ranged weapons
rangeData = XLSX.load('assets/data/weaponStats.xlsx','ranged')
rangeObjects = XLSX.createObjects(RangeWeapon,rangeData)
#Effects
muzzleFlash = p.transform.scale(p.image.load('assets/effects/muzzleFlash_effect.png'), (scale, scale))

#Varuabkes
#curWeapon = meleeObjects['baseballBat_weapon']
curWeapon = rangeObjects['HEMG_weapon']
reloading = False
firing = False
shoot = False
swing = False
#Custom events
RELOAD = p.USEREVENT + 1
FIRING = p.USEREVENT + 2


#Objects
#Doors
#Load and crop Spritesheets
doorFront = Entity.spritesheetCrop2(p.transform.scale(p.image.load('assets/newMaps/objects/world1_doors.png'),(scale*32,scale*4)),scale*4,scale*2)
doorSide = Entity.spritesheetCrop2(p.transform.scale(p.image.load('assets/newMaps/objects/world1_doors_side.png'),(scale*8,scale*10)),scale,scale*5)

doorDict = {'R':[doorSide[i] for i in range(8)],'U':[doorFront[i] for i in range(8)],\
            'L':[doorSide[i] for i in range(8,16)],'D':[doorFront[i] for i in range(8,16)]} #Dict of all the sprites of all the doors

#Variables
doorFrame = 7 #The frame of animation the door is on


#Create clock
clock = p.time.Clock()


#Active game loop =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
running = True
while running:
    
    #Time stepping
    #Update timedelta to maintain constant movement in space and time
    timedelta = clock.tick(60)
    seconds = timedelta/1000  #Convert from milliseconds to seconds
    #Maintain range for deltatime
    if seconds > 50/1000:
        seconds = 50/1000

    #Update counters
    count += 1
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

        #Projectle weapon events
        if isinstance(curWeapon,RangeWeapon) == True:
            #Reload wepaon
            if click and m3 == 1 and reloading == False:
                #start timer for reload
                p.time.set_timer(RELOAD, curWeapon.reloadTime)
                reloading = True

            if evt.type == RELOAD and reloading == True:
                #Refill ammo
                curWeapon.clipCount = curWeapon.clipSize
                reloading = False  # Reset event

            #Weapon firereate delay (cooldown between shots)
            #If weapon has autofire
            if curWeapon.autoFire == True:
                if m1 == 1 and (curWeapon.clipCount == None or curWeapon.clipCount > 0) and reloading == False and firing == False:
                    p.time.set_timer(FIRING, curWeapon.baseAtkRate)
                    firing = True

            elif curWeapon.autoFire == False:
                if click and (curWeapon.clipCount == None or curWeapon.clipCount > 0) and reloading == False and firing == False:
                    p.time.set_timer(FIRING, curWeapon.baseAtkRate)
                    firing = True

            if evt.type == FIRING and firing == True:
                shoot = True
                firing = False  #Reset event
        
        #Melee weapon events
        if isinstance(curWeapon,MeleeWeapon) == True:
            #Melee swinging delay
            if click == True and swing == False:
                swing = True
                #Spawn bullet/slash projectile or whatever
                angle = m.atan2(pos2-centerY, pos1-centerX) #Determine weapon rotate angle relative to mouse pos
                projectileObjects[curWeapon.projectile].spawn(curWeapon.muzzlePos*m.cos(angle)+curPlayer.X, curWeapon.muzzlePos*m.sin(angle)+curPlayer.Y, angle)


    screen.fill((47,40,58)) #Fill background

    #Update Entities =-=-=-=-=-=-=-=-=-=
    #Move player
    #Calculate player pos on room collision map (this pos is the top left of the IMAGE of the player
    playerX, playerY = curPlayer.X-curPlayer.spriteWidth/2, curPlayer.Y-curPlayer.spriteHeight/2
    
    #Determine which map element the player is in
    curChunkX, curChunkY = int(playerX//mapScale), int(playerY//mapScale)

    #Get the collision data for that map element
    mapCollide = map1.mrCollisionData[curChunkY][curChunkX]
    
    #Player movement perdicter (ignores collisions)
    pIsWalking, moveX, moveY = curPlayer.move(seconds)

    #Update the player walking hitbox (This is the rect of the MOVEMENT COLLISION BOX)
    movePlayerRect = p.Rect(playerX+curPlayer.cRect[0], playerY+curPlayer.cRect[1], curPlayer.cRect[2], curPlayer.cRect[3])
    #Find all the collision objects that are close to the player
    collideList = Collider.localCollision(curChunkX,curChunkY,movePlayerRect,mapCollide,scale,numOfElements)

    #Break up the player movement into 'components' and determine which axis is colliding
    xoffset, yoffset = True, True #Axis locks
    newPlayerRectX = p.Rect(movePlayerRect[0]+moveX,movePlayerRect[1],movePlayerRect[2],movePlayerRect[3])
    newPlayerRectY = p.Rect(movePlayerRect[0],movePlayerRect[1]+moveY,movePlayerRect[2],movePlayerRect[3])
    
    #Check to see if the player collides with anything near it
    for i in range(len(collideList)):
        if newPlayerRectX.colliderect(collideList[i]) == True:
            xoffset = False

        elif newPlayerRectY.colliderect(collideList[i]) == True:
            yoffset = False

    #Move player
    if xoffset == True:
        curPlayer.X += moveX
    if yoffset == True:
        curPlayer.Y += moveY
    
    #Player Projectile Hitbox
    #Determine the frame of animation the player is on
    animatedPic = curPlayer.animate(pIsWalking,count) #Update player animation
    #Flip player depending on mouse pos
    if pos1 < centerX:
        pflip = p.transform.flip(animatedPic,True,False)
    else:
        pflip = animatedPic
    
    #Update offset
    curPlayer.shiftX, curPlayer.shiftY = -curPlayer.X+Setup.centerX, -curPlayer.Y+Setup.centerY


    #Move Enemies

    
    #Draw Map =-=-=-=-=-=-=-=-=-=
    #Chunk loading
    #Determine which map elements are within seeing range of character
    #Find the levelMap coordinates of the top left most map element that can be seen
    TLRoomX, TLRoomY = int((curPlayer.X-screenX/2)/mapScale), int((curPlayer.Y-screenY/2)/mapScale) #Top left corner of screen
    BRRoomX, BRRoomY = int((curPlayer.X+screenX/2)/mapScale), int((curPlayer.Y+screenY/2)/mapScale) #Bot right corner of screen

    #Amount of map elements the camera can sees
    loadX, loadY = BRRoomX-TLRoomX+1, BRRoomY-TLRoomY+1

    #Layer1 - Draw the room on the visible chunks
    for i in range(loadY):
        for n in range(loadX):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(map1.levelMap) and 0 <= TLRoomY+i < len(map1.levelMap):
                #Draw room
                scalepic = map1.levelMap[TLRoomY+i][TLRoomX+n][-1]
                screen.blit(scalepic, ((TLRoomX+n)*mapScale+curPlayer.shiftX, (TLRoomY+i)*mapScale+curPlayer.shiftY)) #Move map depending on camera location
                
                #Draw room layout
                if map1.layoutMap[TLRoomY+i][TLRoomX+n] != []:
                    scalepic = map1.layoutMap[TLRoomY+i][TLRoomX+n][-1]
                    screen.blit(scalepic, ((TLRoomX+n)*mapScale+curPlayer.shiftX, (TLRoomY+i)*mapScale+curPlayer.shiftY)) #Move map depending on camera location

    #Layer2 - Draw the objects on the visible chunks
    for i in range(loadY):
        for n in range(loadX):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(map1.levelMap) and 0 <= TLRoomY+i < len(map1.levelMap):
                #Draw doors
                if map1.doorPosList[TLRoomY+i][TLRoomX+n] != None: #If there are doors in this map element
                    for d in range(len(map1.doorPosList[TLRoomY+i][TLRoomX+n])): #For each door in room
                        scalepic = doorDict[map1.doorPosList[TLRoomY+i][TLRoomX+n][d][0]][doorFrame] #Determine which way the door is facing
                        screen.blit(scalepic, (map1.doorPosList[TLRoomY+i][TLRoomX+n][d][1]+curPlayer.shiftX, map1.doorPosList[TLRoomY+i][TLRoomX+n][d][2]+curPlayer.shiftY)) #Move dors depending on camera location          
                        
    #Update Projectiles =-=-=-=-=-=-=-=-=-=
                    
    #Draw the player before the projectiles and weapons
    screen.blit(pflip,(curPlayer.X+curPlayer.shiftX-curPlayer.spriteWidth/2,curPlayer.Y+curPlayer.shiftY-curPlayer.spriteHeight/2)) #Draw Player in center of the screen


    #Player Projectiles
    #Range weapons
    if isinstance(curWeapon,RangeWeapon) == True: #Make sure that weapon is allowed to shoot projectiles
        #Shoot weapon
        #Spawn bullet
        if shoot == True:

            for i in range(curWeapon.shots):
                angle = m.atan2(pos2-centerY, pos1-centerX) #Determine weapon rotate angle relative to mouse pos
                #Generate a random offset angle for bullet within range of gun's spread
                bulletSpread = m.radians(r.randint(-curWeapon.spread, curWeapon.spread))
                angle += bulletSpread  #Apply bullet spread
                projectileObjects[curWeapon.projectile].spawn(curWeapon.muzzlePos*m.cos(angle)+curPlayer.X, curWeapon.muzzlePos*m.sin(angle)+curPlayer.Y, angle)
                #Each time a projectile is spawned, reduce number of ammo left
                if curWeapon.clipCount != None:
                    curWeapon.clipCount -= 1
                    if curWeapon.clipCount <= 0: #Dont shoot all shots if clip runs out
                        break

            #Draw muzzle flash
            rpic = p.transform.rotate(muzzleFlash, m.degrees(-angle))
            screen.blit(rpic, (centerX+(curWeapon.muzzlePos)*m.cos(angle)-rpic.get_width()/2, centerY+(curWeapon.muzzlePos)*m.sin(angle)-rpic.get_height()/2))

            shoot = False

        rsurface = curWeapon.rotate(pos1,pos2,centerX,centerY,curWeapon.centerX,curWeapon.centerY) #Rotate weapon
        screen.blit(rsurface,(centerX-rsurface.get_width()/2,centerY-rsurface.get_height()/2)) #Draw weapon


    #Melee Weapon
    if isinstance(curWeapon,MeleeWeapon) == True:

        #Swing weapon, but make sure that the weapon isnt already being swung
        if swing == True:

            #Add the rotation angle to the mouse angle
            rsurface = curWeapon.meleeSwing(pos1,pos2,centerX,centerY)
            screen.blit(rsurface, (centerX-rsurface.get_width()/2,centerY-rsurface.get_height()/2)) #Draw the rotated weapon

            #Check to see when the swing is over and reset the swing variables
            if curWeapon.swingMode == 3:
                swing = False
                curWeapon.swingMode = 0
                
        #Draw the melee weapon only if the weapon isnt being swung
        elif swing == False:
            rsurface = curWeapon.rotate(pos1,pos2,centerX,centerY,curWeapon.centerX,curWeapon.centerY) #Rotate weapon
            screen.blit(rsurface,(centerX-rsurface.get_width()/2,centerY-rsurface.get_height()/2)) #Draw weapon


    #Projectiles    
    playerBoundRectList = [] #list to hold all bounding rects of projectiles
    playerBoundLocalColls = [] #List to hold all lists of local collisions near each projectile
    #Update each projectile
    if len(projectileObjects[curWeapon.projectile].posList) > 0:
        projectileObjects[curWeapon.projectile].update(seconds)  #Update position of all projectiles on map
        for i in range(len(projectileObjects[curWeapon.projectile].posList)):
            #Draw all projectiles
            bulletX, bulletY = projectileObjects[curWeapon.projectile].posList[i][0]-projectileObjects[curWeapon.projectile].imageList[i].get_width()/2, projectileObjects[curWeapon.projectile].posList[i][1]-projectileObjects[curWeapon.projectile].imageList[i].get_height()/2
            screen.blit(projectileObjects[curWeapon.projectile].imageList[i],(bulletX+curPlayer.shiftX,bulletY+curPlayer.shiftY))
            #Get bounding rect of projectile
            picRect = Collider.getBoundingRect(projectileObjects[curWeapon.projectile].imageList[i]) #Get bounding rect of surface
            boundRect = p.Rect(bulletX+picRect[0],bulletY+picRect[1],picRect[2],picRect[3]) #Add blit position to bounding rect
            playerBoundRectList.append(boundRect)

            #Find local collisions of each projectile
            playerBoundLocalColls.append(Collider.localCollision(curChunkX,curChunkY,boundRect,mapCollide,scale,numOfElements))

    #Check to see if any projectiles need to be 'killed'
    killList = []

    for i in range(len(playerBoundRectList)): #For each projectile...
        
        #Check to see if any projectiles hit any map collisions
        for n in range(len(playerBoundLocalColls[i])): #For each local collision object
            if playerBoundRectList[i].colliderect(playerBoundLocalColls[i][n]) == True: #Check to see if projectile collides with anything
                killList.append(i) #add projectile to kill list
                break
        '''
        #Check to see if any projectiles are off of the map by checking its top-left corner and bottom-right corner
        if not 0 <= playerBoundRectList[i][0]-curChunkX*numOfElements*scale < mapScale \
           or not 0 <= playerBoundRectList[i][1]-curChunkY*numOfElements*scale < mapScale \
           or not 0 <= playerBoundRectList[i][0]+playerBoundRectList[i][2]-curChunkX*numOfElements*scale < mapScale \
           or not 0 <= playerBoundRectList[i][1]+playerBoundRectList[i][3]-curChunkY*numOfElements*scale < mapScale:
            if i not in killList: #Don't try to kill same projectile twice
                killList.append(i) #add projectile to kill list
        '''
        
    #Kill projectiles that need to be killed
    projectileObjects[curWeapon.projectile].kill(killList)

    #Visually update the position of all projectiles on map
    for i in range(len(projectileObjects[curWeapon.projectile].posList)):
        screen.blit(projectileObjects[curWeapon.projectile].imageList[i], (projectileObjects[curWeapon.projectile].posList[i][0]-projectileObjects[curWeapon.projectile].imageList[i].get_width()/2, projectileObjects[curWeapon.projectile].posList[i][1]-projectileObjects[curWeapon.projectile].imageList[i].get_height()/2))

    #p.draw.rect(screen,(0,255,0),(20,35,10,10))
        
    p.display.flip()
    
p.quit()
