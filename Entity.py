#Daniel Liu
import pygame as p
import math as m
import random as r
import Setup
from pprint import *
from Collider import *
from Projectile import *
from Pathfinding import *
from XLSX import *

#The entity class handles the entity's stats, animation and collisions
class Entity:

    def __init__(self,name,spritesheet,spriteWidth,spriteHeight,numOfIdle,numOfMove,cRect,speed):
        #self.X, self.Y = entityX, entityY #Spawn position of entity
        self.name = name
        self.spritesheet = spritesheet #Raw pictures
        self.idleList, self.walkList = [], [] #List of animations
        self.spriteWidth, self.spriteHeight = spriteWidth, spriteHeight #Size of each sprite
        self.numOfIdle, self.numOfMove = numOfIdle, numOfMove #Number of idle frames and moving frames
        self.cRect = tuple([int(i) for i in cRect.split(',')]) #Walking collision rect
        self.speed = speed #pixel per second
        
        
        
    
    #ANIMATION FUNCTIONS =-=-=-=-=-=-=-=-=-=-=-=-=
    #First row  is always idle frames, second row is always walking frames
    def spritesheetCrop(self): #Take in a spritesheet and cut into sprites that are returned in a list
        spritesheetWidth, spritesheetHeight = self.spritesheet.get_width(), self.spritesheet.get_height() 
        ispriteWidth, ispriteHeight = Setup.playerScale, Setup.playerScale
        spriteList = [[None for i in range(spritesheetWidth//self.spriteWidth)] for n in range(spritesheetHeight//self.spriteHeight)] #List to hold all cropped out sprites
        for n in range(spritesheetHeight//ispriteHeight): #For each sprite
            for i in range(spritesheetWidth//ispriteWidth): #Interger divison  makes sure that all cropped sprites are the same size            
                #Subsurface the spritesheet
                spriteList[n][i] = (self.spritesheet.subsurface(i*ispriteWidth,n*ispriteHeight,ispriteWidth,ispriteHeight))

        #Add sprites to walk and idle lists)
        #Put all idle momevemt frames into a list
        for i in range(self.numOfIdle):
            self.idleList.append(spriteList[0][i])
        #Put all movement frames into a list
        for i in range(self.numOfMove):
            self.walkList.append(spriteList[1][i])


    @staticmethod
    #Utility version of Entity.spritesheetCrop, for other animated sprites
    def spritesheetCrop2(spritesheet,spriteWidth,spriteHeight): #Take in a spritesheet and cut into sprites that are returned in a list
        spritesheetWidth, spritesheetHeight = spritesheet.get_width(), spritesheet.get_height()
        spriteList = [] #List to hold all cropped out sprites
        for n in range(spritesheetHeight//spriteHeight): #For each sprite
            for i in range(spritesheetWidth//spriteWidth): #Interger divison  makes sure that all cropped sprites are the same size            
                #Subsurface the spritesheet
                spriteList.append(spritesheet.subsurface(i*spriteWidth,n*spriteHeight,spriteWidth,spriteHeight))

        return spriteList


    @staticmethod
    #Gets the pos of the chunk the enemy is spawned at
    def spawnEntities(collList):
        spawnList = []
        for i in range(len(collList)): #Iterate through list
            for n in range(len(collList[i])):
                if collList[i][n] != []:
                    if int(collList[i][n][0]) == 4: #If the tile is a enemy spawn
                        spawnList.append((n,i))

        return spawnList
    
    
    #Animates the player depending on wether or not the player is moving
    def animate(self,isWalking,count):

        #Do idle animation if entity is not moving
        if isWalking == False:
            if count%self.idleAniSpeed == 0:
                #Update frame
                self.idleFrame += 1
                if self.idleFrame >= len(self.idleList):
                    self.idleFrame = 0
            animatedPic = self.idleList[self.idleFrame]
    
        #Do walking animation if entity is moving
        else:
            #Limit animation rate
            if count%self.walkAniSpeed == 0:
                #Update frame
                self.walkFrame += 1
                if self.walkFrame >= len(self.walkList):
                    self.walkFrame = 0
            animatedPic = self.walkList[self.walkFrame]

        return animatedPic


class Player(Entity):

    def __init__(self,name,spritesheet,spriteWidth,spriteHeight,numOfIdle,numOfMove,cRect,speed,hp):
        super().__init__(name,spritesheet,spriteWidth,spriteHeight,numOfIdle,numOfMove,cRect,speed)
        self.X, self.Y = 0, 0 #Spawn position of entity
        self.shiftX, self.shiftY = -self.X+Setup.centerX/2-Setup.playerScale/2,-self.Y+Setup.centerY-Setup.playerScale/2
        self.hp = hp

        #Create player sprites  
        self.spritesheet = p.transform.scale(p.image.load(spritesheet),(spriteWidth*Setup.playerScale,spriteHeight*Setup.playerScale))
        self.spritesheetCrop() #Crop Sprite

        #Animation variables
        self.idleAniSpeed = 24 #Speed frame cycle of idle animation
        self.walkAniSpeed = 4 #Speed frame cycle of walking animation
        self.idleFrame, self.walkFrame = 0, 0
        
    def move(self,currentTimeDelta):
        POFFX, POFFY = 0, 0 #Player direction variables
        moveX, moveY = 0, 0 #The distance the player moves when ignoring collisions
        #Determine direction of movement
        if p.key.get_pressed()[p.K_d]: #Right
            POFFX = 1
        if p.key.get_pressed()[p.K_w]: #Up
            POFFY = -1
        if p.key.get_pressed()[p.K_a]: #Left
            POFFX = -1
        if p.key.get_pressed()[p.K_s]: #Down
            POFFY = 1

        #Move player
        if (POFFX, POFFY) != (0, 0):
            angle = m.atan2(POFFY,POFFX)
            #Vary pixel per update depending on time it took for previous update
            moveX = self.speed*currentTimeDelta*m.cos(angle)
            moveY = self.speed*currentTimeDelta*m.sin(angle)
            #The player isnt actually moved, the function just returns the move distance
            
            isWalking = True #If the player is moving
        else:
            isWalking = False

        return isWalking, moveX, moveY #return movement distance as it may need to be reversed later if the player collides with something
        

class Enemy(Entity):

    direct = [(0,0),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)] #The potential directions the enemy could be headed in
    
    def __init__(self,name,spritesheet,spriteWidth,spriteHeight,numOfIdle,numOfMove,cRect,speed,hp):
        super().__init__(name,spritesheet,spriteWidth,spriteHeight,numOfIdle,numOfMove,cRect,speed)

        self.hp = hp
                
        #Graphical aspect of enemies
        self.hpList = [] #The current health of all the enemies of this type
        self.imageList = [] #The current frame of animation all the enemies of this type is on
        self.posList = [] #The current position of all the enemies of this type
        self.directList = [] #List of the current direction the enemy is heading in
        self.countList = [] #List of counters used for animation
        #Create enemy sprites
        self.spritesheet = p.transform.scale(p.image.load(spritesheet),(spriteWidth*Setup.playerScale,spriteHeight*Setup.playerScale))
        self.spritesheetCrop() #Crop Sprite

        #Animation variables
        self.idleAniSpeed = 24 #Speed frame cycle of idle animation
        self.walkAniSpeed = 20 #Speed frame cycle of walking animation
        self.idleFrame, self.walkFrame = 0, 0
            
    def spawn(self,spawnX,spawnY): #Create a new enemy
        self.hpList.append(self.hp) #New enemy starts with the base hp
        self.posList.append((int(spawnX),int(spawnY))) #Spawnpoint of enemy
        self.imageList.append(self.idleList[0]) #Default sprite of enemy is idle
        self.directList.append(r.choice(Enemy.direct))
        self.countList.append(0)
        
    def kill(self,killList): #Deletes enemies
        #Use list comprehension to create a new list with only the enemies that shuldnt be deleted
        self.hpList[:] = [self.hpList[i] for i in range(len(self.hpList)) if i not in killList]
        self.imageList[:] = [self.imageList[i] for i in range(len(self.imageList)) if i not in killList]
        self.posList[:] = [self.posList[i] for i in range(len(self.posList)) if i not in killList]
        self.directList[:] = [self.directList[i] for i in range(len(self.directList)) if i not in killList]
        self.countList[:] = [self.countList[i] for i in range(len(self.countList)) if i not in killList]


    #Use a* algorithm to find path to destination
    def path(self,grid,elementSize,destX,destY,enemyIndex):

        #Round enemy position and destination to nearest map element
        selfX, selfY = int(self.enemyPosList[enemyIndex][0]/elementSize), int(self.enemyPosList[enemyIndex][1]/elementSize)
        destX, destY = int(destX/elementSize), int(destY/elementSize) 

        pathList = Pathfinding.shortestpath(selfX,selfY,destX,destY,grid)

        #Create a list of movement directions
        directList = []
        for i in range(len(pathList)-1):
            directList.append((pathList[i][0]-pathList[i+1][0],pathList[i][1]-pathList[i+1][1]))
        
        return directList, pathList, selfX, selfY,destX, destY

    '''
    #Return a list of future enemy positions without checking for collisions
    #This function moves individual entities
    def move(self,moves,currentTimeDelta):
        moveX, moveY = 0, 0
    '''
    '''
    #Move enemies in a random direction until it hits a collision object
    def roamMove(self,currentTimeDelta,index):
        #print(self.directList[index][0], self.directList[index][1])
        EOFFX, EOFFY = self.directList[index][0], self.directList[index][1] #Direction enemy is moving in
        moveX, moveY = 0, 0
        
        #if the enemy is standing still
        if EOFFX == 0 and EOFFY == 0:
            isWalking = False #Set animation mode to idle
            #Give a random chance for the enemy to start moving again
            moveChance = r.randint(0,75)
            if moveChance == 0:
                self.directList[index] = r.choice(Enemy.direct) #Choose a new random directinon for enemy to move in
        else: #if the enemy is moving
            isWalking = False #Set animation mode to moving
            angle = m.atan2(EOFFY,EOFFX) #Find the angle the enemy is moving at
            #Vary pixel per update depending on time it took for previous update
            moveX = self.speed*currentTimeDelta*m.cos(angle)
            moveY = self.speed*currentTimeDelta*m.sin(angle)

        return isWalking, moveX, moveY

    
    #Move enemies in a random direction until it hits a collision object
    def roamMove(self,currentTimeDelta,index):
        #print(self.directList[index][0], self.directList[index][1])
        EOFFX, EOFFY = self.directList[index][0], self.directList[index][1] #Direction enemy is moving in
        moveX, moveY = 0, 0
        
        #if the enemy is standing still
        if EOFFX == 0 and EOFFY == 0:
            isWalking = False #Set animation mode to idle
            #Give a random chance for the enemy to start moving again
            moveChance = r.randint(0,25)
            if moveChance == 0:
                self.directList[index] = r.choice(Enemy.direct) #Choose a new random directinon for enemy to move in
        else: #if the enemy is moving
            isWalking = False #Set animation mode to moving
            angle = m.atan2(EOFFY,EOFFX) #Find the angle the enemy is moving at
            #Vary pixel per update depending on time it took for previous update
            moveX = self.speed*currentTimeDelta*m.cos(angle)
            moveY = self.speed*currentTimeDelta*m.sin(angle)

        return isWalking, moveX, moveY
        '''

'''
#Scale Variables
scale = 32
playerScale = 50

#Init calls
p.init()

#Set up screen
screenX, screenY = 800,600
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = int(screenX/2), int(screenY/2)


#Import assets
#Entities
#Players
#Load spritesheets
martialArtistSprite = p.transform.scale(p.image.load('assets/entities/martialArtist_spritesheet.png'), (5*playerScale, 2*playerScale))
knightSprite = knightSprite = p.transform.scale(p.image.load('assets/entities/templeKnight_spritesheet.png'), (5*playerScale, 2*playerScale))

px, py = 400, 300 #player starting coords (should be in the center of the spawn room)

#Create players
martialArtist = Player(martialArtistSprite,playerScale,playerScale,(20,35,10,10),100,200,px-centerX+scale/2,py-centerY+scale/2)
knight = Player(knightSprite,playerScale,playerScale,(20,35,10,10),120,250,px-centerX+scale/2,py-centerY+scale/2)
#Crop player sprites
martialArtist.spritesheetCrop(2,5)
knight.spritesheetCrop(2,5)

curPlayer = martialArtist




#Create collide objects
#Create collision data sheet for map objects
#rawMapCollide = Collider.importCollisionMap('assets/maps/collisions/room_coll.txt',scale,16) #Import raw collisions data
rawMapCollide = Collider.importCollisionMap('assets/maps/collisions/room_coll_pftest.txt',scale,16) #Import raw collisions data
mapCollide = Collider.convertCollisionGrid(rawMapCollide,scale,16) #Covert collision data into collision rect objects
#Create collision data sheet for projectile objects
playerProjCollide = Collider.convertCollisionGrid([],scale,16)
enemyProjCollide = Collider.convertCollisionGrid([],scale,16)
#Create collision data sheet for pathfinding ai

#pprint(Pathfinding.simplify(mapCollide))
movementGrid = Pathfinding.graph(Pathfinding.simplify(mapCollide))


#Create clock
clock = p.time.Clock()



#vars
count = 0

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


    #Player movement
    #Calculate player movement perdicter (ignore collisions)
    pIsWalking, moveX, moveY = curPlayer.move(seconds)

    #Calculate player pos on room collision map (this pos is the top left of the IMAGE of the player
    playerX, playerY = curPlayer.X+(centerX-curPlayer.spriteWidth/2), curPlayer.Y+(centerY-curPlayer.spriteHeight/2)
    
    
    #Player walking hitbox
    #Update player rect (this pos is the position of the movement COLLISION BOX of the player)
    movePlayerRect = p.Rect(playerX+curPlayer.cRect[0], playerY+curPlayer.cRect[1], curPlayer.cRect[2], curPlayer.cRect[3])
    #Find all collisions that are close to the player
    collideList = Collider.localCollision(movePlayerRect,mapCollide,scale)


    xoffset, yoffset = True, True
    #break up the player movement into 'components' and determine which axis is colliding
    newPlayerRectX = p.Rect(movePlayerRect[0]+moveX,movePlayerRect[1],movePlayerRect[2],movePlayerRect[3])
    newPlayerRectY = p.Rect(movePlayerRect[0],movePlayerRect[1]+moveY,movePlayerRect[2],movePlayerRect[3])
    
    #Check to see if the player collides with anything near it
    for i in range(len(collideList)):
        if newPlayerRectX.colliderect(collideList[i]) == True:
            xoffset = False

        elif newPlayerRectY.colliderect(collideList[i]) == True:
            yoffset = False

    #move player
    if xoffset == True:
        curPlayer.X += moveX
    if yoffset == True:
        curPlayer.Y += moveY

        
    #Player projectile hitbox
    #determine frame of animation the player is on
    animatedPic = curPlayer.animate(pIsWalking,count) #Update player animation
    #Flip player depending on mouse pos
    if pos1 < centerX:
        pflip = p.transform.flip(animatedPic,True,False)
    else:
        pflip = animatedPic
    
    #Get bounding rect of frame (as projectile collisions need to be more accurate)
    hitbox = Collider.getBoundingRect(pflip)
    #Update player hitbox rect (this pos is the position of the projectile COLLISION BOX of the player)
    playerHitbox = p.Rect(playerX+hitbox[0], playerY+hitbox[1], hitbox[2], hitbox[3])
    #Find all projectiles that are close to the player
    #enemyProjList = Collider.localCollision(playerHitbox,enemyProjCollide,scale)

    
    #Update screen
    #Fill screen
    screen.fill((100,100,100))
    #Shift map depending on how much the player is moving
    screen.blit(demoMap, (-curPlayer.X, -curPlayer.Y))

    
    #Player
    screen.blit(pflip,(centerX-pflip.get_width()/2,centerY-pflip.get_height()/2)) #Draw Player in center of the screen

    p.display.flip()

p.quit()      
'''
