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


'''
The pathfinding system broke so I had to create a crappy combat system
where enemies don't have collisions as filler :(
'''

#Scale Variables
scale = Setup.scale
mapScale = Setup.mapScale
playerScale = Setup.playerScale

#Init calls
p.init()
p.mixer.init()
p.font.init()
MapGen.initGraphics(mapScale) #Load map images

#Set up screen
screenX, screenY = Setup.screenX, Setup.screenY
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = Setup.centerX, Setup.centerY
screen.set_alpha(None)
#Set up window
p.display.set_icon(p.image.load('assets/ui/logo.png'))
p.display.set_caption("Pixel Dungeon")


#Object Setups =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#Create Map
curMap = {} #Holds all of the floor data
numOfElements = 16
floor = 0 #The floor the player is on
complexityScale = 2.5 #How complicated the floor is
descend = True #Generate new map on startup


#Players
playerData =  XLSX.load('assets/data/entityStats.xlsx','player')
playerObjects = XLSX.createObjects(Player,playerData)

#Variables
#Randomize player
chosenPlayer = r.choice(['martialArtist','knight'])
curPlayer = playerObjects[chosenPlayer]

count = 0


#Enemies
#Load spritesheets
enemyData = XLSX.load('assets/data/entityStats.xlsx','enemy')
enemyObjects = XLSX.createObjects(Enemy,enemyData)


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
#Choosen random starting weapon
weaponType = r.randint(0,5)
if weaponType == 0:
    curWeapon = meleeObjects[r.choice(list(meleeObjects))]
else:
    curWeapon = rangeObjects[r.choice(list(rangeObjects))]
#curWeapon = meleeObjects['photonsaber_weapon']
#curWeapon = rangeObjects['trident_weapon']
reloading = False
firing = False
shoot = False
swing = False
weaponOffX, weaponOffY = 0, playerScale//4 #how much the weapon is offsetted relative to the center
weaponX, weaponY = centerX+weaponOffX, centerY+weaponOffY #Actual blit position of weapon
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

ANIMATEDOOR = p.USEREVENT + 3 #periodically animate door

#Variables
doorFrame = 7 #The frame of animation the door is on
objectColls = [] #Extra collision objects other entities
doorAniSpeed = 32 #Speed at which the door opens/closes
doorMode = 'close' #Type of animation

#Chests
#Load and crop spritesheet
chestSprites = Entity.spritesheetCrop2(p.transform.scale(p.image.load('assets/newMaps/objects/chest.png'),(scale*6,scale)),scale,scale)
chestAniSpeed = 24
ANIMATECHEST = p.USEREVENT + 4

#Variables
doorAniSpeed = 32 #Speed at which the chest opens

#UI
#Import images
#Key info
key_E = p.transform.scale(p.image.load('assets/ui/key_E.png'),(scale,scale))
interactE = False

ammoPic = p.transform.scale(p.image.load('assets/ui/ammoIcon.png'),(scale,scale))
noAmmoPic = p.transform.scale(p.image.load('assets/ui/noAmmoIcon.png'),(scale,scale))
reloadPic = p.transform.scale(p.image.load('assets/ui/reloadIcon.png'),(scale,scale))

#UI objects
weaponRarity = ['Common','Uncommon','Rare','Epic','Legendary']
weaponDisplay = {i:p.transform.scale(p.image.load('assets/ui/weaponDisplay'+i+'.png'),(int(scale*1.5),int(scale*1.5))) for i in weaponRarity}
weaponPic = p.transform.scale(curWeapon.image, (int(scale*1.5),int(scale*1.5)))
hpbarMartialArtist = p.transform.scale(p.image.load('assets/ui/hpBarMartialArtist.png'),(scale*4,scale*2))
hpbarKnight = p.transform.scale(p.image.load('assets/ui/hpBarKnight.png'),(scale*4,scale*2))
#UI text
gameFont = p.font.SysFont('arialbold',16)
ammoFont = p.font.SysFont('arialbold',32)
curWeaponText = gameFont.render(curWeapon.name, True, (255,255,255))
ammoTextDict = {str(i):(ammoFont.render(str(i), True, (255,255,255))) for i in range(10)}
ammoTextDict['/'] = ammoFont.render('/', True, (255,255,255))
ammoTextDict['-'] = ammoFont.render('-', True, (255,255,255))
        
#Create clock
clock = p.time.Clock()


#Load music
musicList = ['Another Medium','ASGORE','Battle Against a True Hero','Core','Death by Glamour','Megalovania','Toriel Theme']
#Pick a random song
songChoice = r.choice(musicList)
p.mixer.music.load('assets/sounds/Undertale - '+songChoice+'.mp3')
p.mixer.music.play(-1)
print('Now playing', songChoice)

#Active game loop =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
running = True
while running:
    
    #Time stepping
    #Update timedelta to maintain constant movement in space and time
    timedelta = clock.tick(30)
    seconds = timedelta/1000  #Convert from milliseconds to seconds
    #Maintain range for deltatime
    if seconds > 1000/1000:
        seconds = 1000/1000

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
            if ((click and m3 == 1) or (p.key.get_pressed()[p.K_r])) and reloading == False and curWeapon.clipSize != None:
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
                projectileObjects[curWeapon.projectile].spawn(curWeapon.muzzlePos*m.cos(angle)+curPlayer.X+weaponOffX, curWeapon.muzzlePos*m.sin(angle)+curPlayer.Y+weaponOffY, angle)

        #Animations
        #Animate doors
        if evt.type == ANIMATEDOOR:
            if doorMode == 'close':
                doorFrame -= 1
            elif doorMode == 'open':
                doorFrame += 1
            #Limit door frames
            if doorFrame > 7:
                doorFrame = 7
            elif doorFrame < 0:
                doorFrame = 0

        if evt.type == ANIMATECHEST and curChest != None:
            chestPics[curChest] += 1
            #Limit chest frames
            if chestPics[curChest] >= 5:
                chestPics[curChest] = 5
                
    #Load map =-=-=-=-=-=-=-=-=-=
    if descend == True:
        #Loading screen
        screen.fill((0,0,0))
        p.display.flip()
        #Create new floor
        floor += 1 #Update floor name
        curFloor = 'map'+str(floor)
        complexityScale += 0.2 #Make new floor slightly larger and more complex
        descend = False #Generate new map
        curMap[curFloor] = MapGen(numOfElements,complexityScale) #Create the map for the new floor

        curMap[curFloor].mrGenny() #Generate the room layout
        curMap[curFloor].mrClassy() #Determine the type of room depending on the amount of exits has
        curMap[curFloor].mrRoomy() #Generate the room layout of each room
        curMap[curFloor].mrCollidey() #Merge the collsion data of the room and room layout
        curMap[curFloor].mrObby(scale) #Create all the doors

        #Make a 2d array with all the collision data of all the rooms
        for i in range(len(curMap[curFloor].level)): #Iterate through each room of map
            for n in range(len(curMap[curFloor].level[i])):
                rawMapCollide = Collider.importCollisionMap(n,i,numOfElements,curMap[curFloor].roomCollide[i][n],scale) #Create actual rect collision objects
                mapCollide = Collider.convertCollisionGrid(n,i,rawMapCollide,scale,numOfElements)
                curMap[curFloor].mrCollisionData[i][n] = mapCollide
        
        #Determine the coords of the center of the spawn room and exit room
        for i in range(len(curMap[curFloor].level)):
            for n in range(len(curMap[curFloor].level[i])):
                if curMap[curFloor].level[i][n] == 5: #If the room is a spawn room
                    spawnroomX, spawnroomY = n*mapScale+mapScale/2, i*mapScale+mapScale/2
                elif curMap[curFloor].level[i][n] == 6: #If the room is an exit room
                    exitroomX, exitroomY = n*mapScale+mapScale/2, i*mapScale+mapScale/2
                    exitChunkX, exitChunkY = n, i #The chunk with the exit room

        #Determine the location and rect of the exit
        exitRect = p.Rect(exitroomX-scale,exitroomY-scale,scale*2,scale*2)

        #Update player position   
        curPlayer.X, curPlayer.Y = spawnroomX, spawnroomY #player starting coords (should be in the center of the spawn room)

        descend = False #Finished generating new floor

        chestPics = [0 for i in range(len(curMap[curFloor].chestPosList))] #Current animation frame of each chest on map
        chestState = ['closed' for i in range(len(curMap[curFloor].chestPosList))] #Chest open/closed
        curChest = None #Current chest player is opening

        floorText = 'Floor '+str(floor) #For ui showing current floor level
        
        print(floorText)
        pprint(curMap[curFloor].level)
        
        floorText = ammoFont.render(floorText, True, (255,255,255)) 



    screen.fill((47,40,58)) #Fill background


    #Update Entities =-=-=-=-=-=-=-=-=-=
    #Move player
    #Calculate player pos on room collision map (this pos is the top left of the IMAGE of the player
    playerX, playerY = curPlayer.X-playerScale/2, curPlayer.Y-playerScale/2

    #Determine which map elements are within seeing range of character
    #Find the levelMap coordinates of the top left most map element that can be seen
    TLRoomX, TLRoomY = int((curPlayer.X-screenX/2)/mapScale), int((curPlayer.Y-screenY/2)/mapScale) #Top left corner of screen
    BRRoomX, BRRoomY = int((curPlayer.X+screenX/2)/mapScale), int((curPlayer.Y+screenY/2)/mapScale) #Bot right corner of screen

    #Amount of map elements the camera can sees
    loadX, loadY = BRRoomX-TLRoomX+1, BRRoomY-TLRoomY+1


    #Check Entity Collisions
    #Determine which map element the player is in
    curChunkX, curChunkY = int(playerX//mapScale), int(playerY//mapScale)

    #Get the collision data for that map element
    mapCollide = curMap[curFloor].mrCollisionData[curChunkY][curChunkX]
    
    #Player movement perdicter (ignores collisions)
    pIsWalking, moveX, moveY = curPlayer.move(seconds)

    #Update the player walking hitbox (This is the rect of the MOVEMENT COLLISION BOX)
    movePlayerRect = p.Rect(playerX+curPlayer.cRect[0], playerY+curPlayer.cRect[1], curPlayer.cRect[2], curPlayer.cRect[3])

    #Find all the collision rects that are close to the player
    collideList = Collider.localCollision(curChunkX,curChunkY,movePlayerRect,mapCollide,scale,numOfElements)
    #Find the collisions rects of all the of the objects that are close to the player
    #Get the collision of surrounding doors
    if doorFrame != 7: #If the doors are closing/closed render the collisions
        for i in range(loadY):
            for n in range(loadX):
                if curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n] != None: #If there are doors in this map element
                    for d in range(len(curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n])): #For each door in room
                        doorCollide = [1,curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n][d][1]]
                        collideList.append(doorCollide) #Add door collision to local collisions to check for
                        objectColls.append(doorCollide) #Add door collisions to other entities
                        
    #Break up the player movement into 'components' and determine which axis is colliding
    xoffset, yoffset = True, True #Axis locks
    newPlayerRectX = p.Rect(movePlayerRect[0]+moveX,movePlayerRect[1],movePlayerRect[2],movePlayerRect[3])
    newPlayerRectY = p.Rect(movePlayerRect[0],movePlayerRect[1]+moveY,movePlayerRect[2],movePlayerRect[3])
    
    #Check to see if the player collides with anything near it
    for i in range(len(collideList)):
        if newPlayerRectX.colliderect(collideList[i][-1]) == True:
            xoffset = False

        elif newPlayerRectY.colliderect(collideList[i][-1]) == True:
            yoffset = False

    #Move player
    if xoffset == True:
        curPlayer.X += moveX
    if yoffset == True:
        curPlayer.Y += moveY

    #Update offset
    curPlayer.shiftX, curPlayer.shiftY = -curPlayer.X+Setup.centerX, -curPlayer.Y+Setup.centerY
    
    #Player Projectile Hitbox
    #Determine the frame of animation the player is on
    animatedPic = curPlayer.animate(pIsWalking,count) #Update player animation
    #Flip player depending on mouse pos
    if pos1 < centerX:
        pflip = p.transform.flip(animatedPic,True,False)
    else:
        pflip = animatedPic


    #Update enemies
    #Spawn entities if the room has not been cleared
    #If the enemies in the room havent been spawned, and the player is not on top of the door, close doors spawn enemies
    
    if curMap[curFloor].progress[curChunkY][curChunkX] == 'unspawned' and playerInteractRect.collidelist([curMap[curFloor].doorPosList[curChunkY][curChunkX][d][1] for d in range(len(curMap[curFloor].doorPosList[curChunkY][curChunkX]))]) == -1: 
        curMap[curFloor].progress[curChunkY][curChunkX] = 'unclear'

        doorMode = 'close'
        for a in range(len(curMap[curFloor].doorPosList[curChunkY][curChunkX])): #Animation for closing doors
            p.time.set_timer(ANIMATEDOOR,a*doorAniSpeed)
            
        #doorFrame = 0
        spawnList = Entity.spawnEntities(mapCollide) #Find the enemy spawn points

        #Spawn new enemies
        newEnemy = enemyObjects[r.choice([enemyData[e]['name'] for e in enemyData])] #Choose a random enemy to spawn
        for i in range(len(spawnList)): #Spawn enemies
            #Determine the spawn position of the new enemy (chunk+tile+middleoftile)
            enSpawnX, enSpawnY = curChunkX*scale*numOfElements+spawnList[i][0]*scale+scale/2, curChunkY*scale*numOfElements+spawnList[i][1]*scale+scale/2
            newEnemy.spawn(enSpawnX,enSpawnY) #Create new enemy
            curMap[curFloor].entities[curChunkY][curChunkX].append(newEnemy) #Add new enemy to floor map
    
    #Move enemies
    for curEnemy in curMap[curFloor].entities[curChunkY][curChunkX]: #For each type of enemy
        for i in range(len(curEnemy.posList)): #For each of that type of enemy
            EOFFX, EOFFY = 0, 0
            if curEnemy.posList[i][0] < curPlayer.X:
                EOFFX = 1
            elif curEnemy.posList[i][0] > curPlayer.X:
                EOFFX = -1
            if curEnemy.posList[i][1] > curPlayer.Y:
                EOFFY = -1
            elif curEnemy.posList[i][1] < curPlayer.Y:
                EOFFY = 1
            angle = m.atan2(EOFFY,EOFFX) #Find the angle the enemy is moving at
            #Vary pixel per update depending on time it took for previous update
            curEnemy.posList[i] = (curEnemy.posList[i][0]+curEnemy.speed*seconds*m.cos(angle),curEnemy.posList[i][1]+curEnemy.speed*seconds*m.sin(angle))

    '''
    for curEnemy in curMap[curFloor].entities[curChunkY][curChunkX]: #For each type of enemy
        
        for i in range(len(curEnemy.posList)): #For each of that type of enemy
            #Implement player-tracking later
            enemyIsWalking,enemyMoveX,enemyMoveY = curEnemy.roamMove(seconds,i) #Predict enemy movement

            #Update enemy movement hitbox
            moveEnemyRect = p.Rect(curEnemy.posList[i][0]+curEnemy.cRect[0],curEnemy.posList[i][1]+curEnemy.cRect[1],curEnemy.cRect[2],curEnemy.cRect[3])

            #Find all collisions that are close to this enemy entitiy
            enemyCollideList = Collider.localCollision(curChunkX,curChunkY,moveEnemyRect,mapCollide,scale,numOfElements)
            
            #Check to see if enemy collides
            for n in range(len(enemyCollideList)):
                if moveEnemyRect.colliderect(enemyCollideList[n][-1]) == True: #If the enemy collides, give a chance to change it's direction
                    moveChance = r.randint(0,25)
                    if moveChance == 0:
                        curEnemy.directList[i] = r.choice(Enemy.direct)
                elif moveEnemyRect.colliderect(enemyCollideList[n][-1]) == False: #If the enemy doesn't collide, move it
                    curEnemy.posList[i] = (curEnemy.posList[i][0]+enemyMoveX,curEnemy.posList[i][1]+enemyMoveY)
    '''
                
    #If all the enemies in the room are dead, open doors
    #if curMap[curFloor].progress[curChunkY][curChunkX] == 'unclear' and  all enemies are dead
    
    #Draw Map =-=-=-=-=-=-=-=-=-=
    #Chunk loading
    #Layer1 - Draw the room on the visible chunks
    for i in range(loadY):
        for n in range(loadX):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(curMap[curFloor].levelMap) and 0 <= TLRoomY+i < len(curMap[curFloor].levelMap):
                #Draw room
                scalepic = curMap[curFloor].levelMap[TLRoomY+i][TLRoomX+n][-1]
                screen.blit(scalepic, ((TLRoomX+n)*mapScale+curPlayer.shiftX, (TLRoomY+i)*mapScale+curPlayer.shiftY)) #Move map depending on camera location
                
                #Draw room layout
                if curMap[curFloor].layoutMap[TLRoomY+i][TLRoomX+n] != []:
                    scalepic = curMap[curFloor].layoutMap[TLRoomY+i][TLRoomX+n][-1]
                    screen.blit(scalepic, ((TLRoomX+n)*mapScale+curPlayer.shiftX, (TLRoomY+i)*mapScale+curPlayer.shiftY)) #Move map depending on camera location

    #Layer2 - Draw the objects on the visible chunks
    for i in range(loadY):
        for n in range(loadX):
            #Make sure that map element is not outside levelMap
            if 0 <= TLRoomX+n < len(curMap[curFloor].levelMap) and 0 <= TLRoomY+i < len(curMap[curFloor].levelMap):
                #Draw doors
                if curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n] != None: #If there are doors in this map element
                    for d in range(len(curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n])): #For each door in room
                        scalepic = doorDict[curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n][d][0]][doorFrame] #Determine which way the door is facing
                        screen.blit(scalepic, (curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n][d][1][0]+curPlayer.shiftX, curMap[curFloor].doorPosList[TLRoomY+i][TLRoomX+n][d][1][1]+curPlayer.shiftY)) #Move dors depending on camera location          
                for c in range(len(curMap[curFloor].chestPosList)):
                    #print(curMap[curFloor].chestPosList[c][0],curMap[curFloor].chestPosList[c][1],loadX,loadY)
                    if curMap[curFloor].chestPosList[c][0] == TLRoomX+n and curMap[curFloor].chestPosList[c][1] == TLRoomY+i: #If there are chests in this map element
                        scalepic = chestSprites[chestPics[c]]
                        screen.blit(scalepic, (curMap[curFloor].chestPosList[c][-1][0]+curPlayer.shiftX, curMap[curFloor].chestPosList[c][-1][1]+curPlayer.shiftY)) #Move chests depending on camera location   

    #Layer3 - UI
    #Draw Keys
    playerInteractRect = p.Rect(curPlayer.X-pflip.get_width()//2,curPlayer.Y-pflip.get_height()//2,pflip.get_width(),pflip.get_height())
    interactE = False
    #Check for environmental interactions
    #If player is going to descend to next floor
    if curChunkX == exitChunkX and curChunkY == exitChunkY: #Is the player in the exit room
        #Check to see if player is colliding with the exit ladder and interaction key is pressed
        if playerInteractRect.colliderect(exitRect) == True:
            #ui - draw e key above payer
            interactE = True
            if (p.key.get_pressed()[p.K_e]):
                descend = True

    #Check to see if player is colliding with the chest
    for c in range(len(curMap[curFloor].chestPosList)): #For each chest in map
        if curMap[curFloor].chestPosList[c][0] == curChunkX and curMap[curFloor].chestPosList[c][1] == curChunkY: #If the player is in the chest room
            #If the player is colliding with the chest and interaction key is pressed
            if playerInteractRect.colliderect(curMap[curFloor].chestPosList[c][-1]) == True and chestState[c] == 'closed':
                #ui - draw e key above player
                interactE = True
                if (p.key.get_pressed()[p.K_e]): #If the playyer presses e, open chest
                    curChest = c #Set current chest
                    chestState[c] = 'open'
                    for a in range(len(chestSprites)): #Animation for opening chest
                        p.time.set_timer(ANIMATECHEST,a*chestAniSpeed)

    #Update Projectiles =-=-=-=-=-=-=-=-=-=
    #Draw the enemies before player
    for curEnemy in curMap[curFloor].entities[curChunkY][curChunkX]: #Draw all enemies
        for i in range(len(curEnemy.posList)):
            enemyIsWalking = True
            curEnemy.countList[i] += 1 #Update animation counter
            aniPic = curEnemy.animate(enemyIsWalking,curEnemy.countList[i])
            screen.blit(aniPic ,(curEnemy.posList[i][0]+curPlayer.shiftX-curEnemy.imageList[i].get_width()/2,curEnemy.posList[i][1]+curPlayer.shiftY-curEnemy.imageList[i].get_height()/2))
            
    #Draw the player before the projectiles and weapons
    screen.blit(pflip,(curPlayer.X+curPlayer.shiftX-playerScale/2,curPlayer.Y+curPlayer.shiftY-playerScale/2)) #Draw Player in center of the screen

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
                projectileObjects[curWeapon.projectile].spawn(curWeapon.muzzlePos*m.cos(angle)+curPlayer.X+weaponOffX, curWeapon.muzzlePos*m.sin(angle)+curPlayer.Y+weaponOffY, angle)
                #Each time a projectile is spawned, reduce number of ammo left
                if curWeapon.clipCount != None:
                    curWeapon.clipCount -= 1
                    if curWeapon.clipCount <= 0: #Dont shoot all shots if clip runs out
                        curWeapon.clipCount = 0
                        break

            #Draw muzzle flash
            rpic = p.transform.rotate(muzzleFlash, m.degrees(-angle))
            screen.blit(rpic, (weaponX+(curWeapon.muzzlePos)*m.cos(angle)-rpic.get_width()/2, weaponY+(curWeapon.muzzlePos)*m.sin(angle)-rpic.get_height()/2))

            shoot = False

        rsurface = curWeapon.rotate(pos1,pos2,centerX,centerY,curWeapon.centerX,curWeapon.centerY) #Rotate weapon
        screen.blit(rsurface,(weaponX-rsurface.get_width()/2,weaponY-rsurface.get_height()/2)) #Draw weapon


    #Melee Weapon
    if isinstance(curWeapon,MeleeWeapon) == True:

        #Swing weapon, but make sure that the weapon isnt already being swung
        if swing == True:

            #Add the rotation angle to the mouse angle
            rsurface = curWeapon.meleeSwing(pos1,pos2,centerX,centerY)
            screen.blit(rsurface, (weaponX-rsurface.get_width()/2,weaponY-rsurface.get_height()/2)) #Draw the rotated weapon

            #Check to see when the swing is over and reset the swing variables
            if curWeapon.swingMode == 3:
                swing = False
                curWeapon.swingMode = 0
                
        #Draw the melee weapon only if the weapon isnt being swung
        elif swing == False:
            rsurface = curWeapon.rotate(pos1,pos2,centerX,centerY,curWeapon.centerX,curWeapon.centerY) #Rotate weapon
            screen.blit(rsurface,(weaponX-rsurface.get_width()/2,weaponY-rsurface.get_height()/2)) #Draw weapon


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
            #Add the collisions of extra objects for projectiles
            for n in range(len(objectColls)):
                playerBoundLocalColls[i].append(objectColls[n])
                
    killList = [] #Check to see if any projectiles need to be 'killed'
    
    for i in range(len(playerBoundRectList)): #For each projectile...
        #Check to see if any projectiles hit any map collisions
        for n in range(len(playerBoundLocalColls[i])): #For each local collision object
            #Check to see if projectile collides with anything and if the object it hits allows projectiles to pass over it
            if playerBoundRectList[i].colliderect(playerBoundLocalColls[i][n][-1]) == True and int(playerBoundLocalColls[i][n][0]) != 2:
                killList.append(i) #add projectile to kill list
                break
            
        #Check to see if any projectiles hit any enemies
        for curEnemy in curMap[curFloor].entities[curChunkY][curChunkX]: #For each enemy in room
            enemyKillList = [] #Check to see if any enemies need to be killed
            for q in range(len(curEnemy.posList)): #For each of the type of enemy
                enemyRect = Collider.getBoundingRect(curEnemy.imageList[q]) #Get the hitbox of enemy
                enemyHitbox = p.Rect(curEnemy.posList[q][0]+enemyRect[0]-curEnemy.imageList[q].get_width()/2,curEnemy.posList[q][1]+enemyRect[1]-curEnemy.imageList[q].get_height()/2,enemyRect[2],enemyRect[3])
                
                #If the bullet hits an enemy, make enemy take damage
                if playerBoundRectList[i].colliderect(enemyHitbox):
                    killList.append(i) #Kill bullet too
                    curEnemy.hpList[q] -= projectileObjects[curWeapon.projectile].dmg
                    if curEnemy.hpList[q] <= 0: #If the enemy's health reaches 0, kill it
                        enemyKillList.append(q)
                    break
                
            #Kill enemies that need to be killed
            curEnemy.kill(enemyKillList) #Remove enemy data from class
            curMap[curFloor].entities[curChunkY][curChunkX][:] = [curMap[curFloor].entities[curChunkY][curChunkX][a] for a in range(len(curMap[curFloor].entities[curChunkY][curChunkX])) if a not in enemyKillList]

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

    #If all enemies are killed, open doors
    if curMap[curFloor].entities[curChunkY][curChunkX] == [] and curMap[curFloor].progress[curChunkY][curChunkX] == 'unclear':
        curMap[curFloor].progress[curChunkY][curChunkX] = 'clear'
        doorMode = 'open'
        for a in range(len(curMap[curFloor].doorPosList[curChunkY][curChunkX])): #Animation for opening doors
            p.time.set_timer(ANIMATEDOOR,a*doorAniSpeed)
            
    #Visually update the position of all projectiles on map
    for i in range(len(projectileObjects[curWeapon.projectile].posList)):
        screen.blit(projectileObjects[curWeapon.projectile].imageList[i], (projectileObjects[curWeapon.projectile].posList[i][0]-projectileObjects[curWeapon.projectile].imageList[i].get_width()/2, projectileObjects[curWeapon.projectile].posList[i][1]-projectileObjects[curWeapon.projectile].imageList[i].get_height()/2))


    #In-Game User Interface =-=-=-=-=-=-=-=-=-=
    
    #Interact info
    if interactE == True:
        screen.blit(key_E, (int(centerX-key_E.get_width()/2),int(centerY-key_E.get_height()/2-playerScale)))
        
    #Draw weapon display
    screen.blit(weaponDisplay[curWeapon.rarity],(screenX-int(scale*4),int(screenY-scale*1.8))) #Draw weapon display border
    screen.blit(weaponPic,(screenX-int(scale*4),int(screenY-scale*1.8))) #Draw weapon preview

    #If the weapon is a projetile weapon
    if isinstance(curWeapon,RangeWeapon) == True and curWeapon.clipSize != None:
        if reloading == True: #If the weapon is reloading
            screen.blit(reloadPic,(screenX-int(scale*2.5),int(screenY-scale*1.5)))
        elif curWeapon.clipCount != 0 or curWeapon.clipCount == None: #If the weapon has ammo
            screen.blit(ammoPic,(screenX-int(scale*2.5),int(screenY-scale*1.5)))
        elif curWeapon.clipCount <= 0: #If the weapon has no more ammo
            screen.blit(noAmmoPic,(screenX-int(scale*2.5),int(screenY-scale*1.5)))
        #Remaining ammunition (for cur ammo text)
        ammoText = [str(curWeapon.clipCount//10),str(curWeapon.clipCount%10),'/',str(curWeapon.clipSize//10),str(curWeapon.clipSize%10)]
    elif isinstance(curWeapon,MeleeWeapon) == True or curWeapon.clipSize == None: #If the weapon is a melee weapon
        screen.blit(ammoPic,(screenX-int(scale*2.5),int(screenY-scale*1.5)))
        #Remaining ammunition (for cur ammo text)
        ammoText = ['-','-','/','-','-']


    #Remaining ammunition text
    for i in range(len(ammoText)):
        screen.blit(ammoTextDict[ammoText[i]],(screenX-int(scale*1.5-scale*i*0.2),int(screenY-scale*1.1)))
    
    #Weapon name
    screen.blit(curWeaponText, (int(screenX-scale*4),int(screenY-scale*0.5)))

    #Hp bar
    if chosenPlayer == 'martialArtist':
        screen.blit(hpbarMartialArtist,(0,0))
    elif chosenPlayer == 'knight':
        screen.blit(hpbarKnight,(0,0))
    
    #Current floor
    screen.blit(floorText, (screenX-floorText.get_width(), 0))
    
    p.display.flip()
    
p.quit()
