import pygame as p
import math as m
import random as r
from Weapon import *
from Projectile import *
from Animate import *
from MapGen import *

scale = 128
roomScale = 128*16
playerScale = 160
weaponScale = 100

p.init()
MapGen.initGraphics(roomScale)

#Set up screen
screenX, screenY = 800,600
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = int(screenX/2), int(screenY/2)
#Import test images =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#Weapons
gun = p.transform.scale(p.image.load('assets/items/hyperEnergyMachineGun_item.png'), (weaponScale, weaponScale))
bat = p.transform.scale(p.image.load('assets/items/woodenBaseballBat_item.png'), (weaponScale, weaponScale))

#Players
playerSprite = p.transform.scale(p.image.load('assets/players/martialArtist_spritesheet.png'), (5*playerScale,2*playerScale))

#Effects (such as projectiles)
bullet = p.transform.scale(p.image.load('assets/effects/hyperEnergyDeathRay_projectile.png'), (weaponScale, weaponScale))
muzzleFlash = p.transform.scale(p.image.load('assets/effects/muzzleFlash_effect.png'), (weaponScale, weaponScale))

#Maps
demoMap = p.transform.scale(p.image.load('assets/maps/room_hub_hub.png'), (roomScale,roomScale))

#Create objects =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#Create character and its animations
#crop spritesheet
spriteList = Animate.spritesheetCrop(playerSprite,playerScale,playerScale)
screen.fill((255,255,255))

#Put all movement frames into a list
walkList = []
for i in range(5):
    walkList.append(spriteList[1][i])
#Put all idle momevemt frames into a list
idleList = []
for i in range(2):
    idleList.append(spriteList[0][i])


#Create new projectiles
testBullet = Projectile(bullet,500,2000,None,None)

# Create new test weapons
HEMG_weapon = Weapon(gun,testBullet,95,7,None,75,None,60,2000)
nav_weapon = MeleeWeapon(bat,0,0,None,None,None,None,None,None)

#Create Map
map1 = MapGen(16,3.2)
MapGen.mrGenny(map1)
map1.mrClassy()
pprint(map1.level)

#Set up camera
cspeed = 400

#Make camera start in middle of start room
for i in range(len(map1.level)):
    for n in range(len(map1.level[i])):
        if map1.level[i][n] == 5:
            playerX, playerY = n*roomScale+roomScale/2, i*roomScale+roomScale/2

#create character instance
susano = Player('martialArtist',playerX,playerY,1000)

#Create clock
clock = p.time.Clock()
    
#vars =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
curWeapon = HEMG_weapon
playerOffsetY = -40

#Weapon
shoot = False
reloading = False
firing = False

#Animation
count = 0
walkFrame = 0
idleFrame = 0

#Custom events
RELOAD = p.USEREVENT + 1
FIRING = p.USEREVENT + 2

#Active loop =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
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

        #Reload wepaon
        if evt.type == p.MOUSEBUTTONDOWN and m3 == 1 and reloading == False:
            #start timer for reload
            p.time.set_timer(RELOAD, curWeapon.reloadTime)
            reloading = True

        if evt.type == RELOAD and reloading == True:
            #Refill ammo
            curWeapon.clipCount = curWeapon.clipSize
            reloading = False  # Reset event

        #Weapon firereate delay
        if m1 == 1 and curWeapon.clipCount > 0 and reloading == False and firing == False:
            p.time.set_timer(FIRING, curWeapon.baseFireRate)
            firing = True

        if evt.type == FIRING and firing == True:
            shoot = True
            firing = False  #Reset event

    #Update screen
    isWalking = susano.move(seconds)

    
    #shift map depending on how much the player is moving
    #Chunk loading
    #Determine which map elements are within seeing range of character
    #Find the levelMap coordinates of the top left most map element that can be seen
    TLRoomX, TLRoomY = round((susano.X-roomScale)/roomScale), round((susano.Y-roomScale)/roomScale)
    
    #Draw the visible chunks (3x3)
    for i in range(3):
        for n in range(3):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(map1.levelMap) and 0 <= TLRoomY+i < len(map1.levelMap):
                #scalepic = p.transform.scale(map1.levelMap[TLRoomY+i][TLRoomX+n][-1], (roomScale,roomScale))
                scalepic = map1.levelMap[TLRoomY+i][TLRoomX+n][-1]
                screen.blit(scalepic, ((TLRoomX+n)*roomScale-susano.X+centerX, (TLRoomY+i)*roomScale-susano.Y+centerY)) #Move map depending on camera location
            else: #Otherwise, if the map element is not on levelMap, assume that it is an empty element
                #scalepic = p.transform.scale(MapGen.otherDict['other'], (roomScale,roomScale))
                scalepic = map1.levelMap[TLRoomY+i][TLRoomX+n][-1]
                screen.blit(scalepic, ((TLRoomX+n)*roomScale-susano.X+centerX, (TLRoomY+i)*roomScale-susano.Y+centerY))
    
    
    if isWalking == True:
        #Limit animation rate
        if count%susano.walkAniSpeed == 0:
            count = 0
            #Update frame
            walkFrame += 1
            if walkFrame >= len(walkList):
                walkFrame = 0
        #shift map depending on how much the player is moving
        #screen.blit(demoMap, (-susano.X, -susano.Y))
        #Flip player depending on mouse pos
        if pos1 < centerX:
            pflip = p.transform.flip(walkList[walkFrame],True,False)
        else:
            pflip = walkList[walkFrame]
        screen.blit(pflip,(centerX-pflip.get_width()/2,centerY-pflip.get_height()/2+playerOffsetY))
    else:
        if count%susano.idleAniSpeed == 0:
            count = 0
            #Update frame
            idleFrame += 1
            if idleFrame >= len(idleList):
                idleFrame = 0
        #shift map depending on how much the player is moving
        #screen.blit(demoMap, (-susano.X, -susano.Y))                
        #Flip player depending on mouse pos
        if pos1 < centerX:
            pflip = p.transform.flip(idleList[idleFrame],True,False)
        else:
            pflip = idleList[idleFrame]
        screen.blit(pflip,(centerX-pflip.get_width()/2,centerY-pflip.get_height()/2+playerOffsetY))
    

    #Shoot weapon
    #Spawn bullet
    if shoot == True:
        angle = m.atan2(pos2-centerY, pos1-centerX)

        #Draw muzzle flash
        rpic = p.transform.rotate(muzzleFlash, m.degrees(-angle))
        screen.blit(rpic, (centerX+(curWeapon.muzzlePos+playerOffsetY)*m.cos(angle)-rpic.get_width()/2, centerY+(curWeapon.muzzlePos+playerOffsetY)*m.sin(angle)-rpic.get_height()/2))

        #Generate a random offset angle for bullet within range of gun's spread
        bulletSpread = m.radians(r.randint(-curWeapon.spread, curWeapon.spread))
        angle += bulletSpread  #Apply bullet spread
        curWeapon.projectile.spawn(centerX+curWeapon.muzzlePos*m.cos(angle), centerY+curWeapon.muzzlePos*m.sin(angle), angle)
        #Each time a projectile is spawned, reduce number of ammo left
        curWeapon.clipCount -= 1

        shoot = False

    #Update each projectile on map according to update rate
    if len(curWeapon.projectile.posList) > 0:
        curWeapon.projectile.update(seconds)  #Update position of all projectiles on map
        #Visually update the position of all projectiles on map
        for i in range(len(curWeapon.projectile.posList)):
            screen.blit(curWeapon.projectile.imageList[i], (curWeapon.projectile.posList[i][0]-curWeapon.projectile.imageList[i].get_width()/2, curWeapon.projectile.posList[i][1]-curWeapon.projectile.imageList[i].get_height()/2))


    #Draw weapon
    rsurface = curWeapon.rotate(pos1,pos2,centerX,centerY,0,0) #Rotate weapon
    screen.blit(rsurface,(centerX-rsurface.get_width()/2,centerY-rsurface.get_height()/2)) #Draw weapon

    p.display.flip()

p.quit()

