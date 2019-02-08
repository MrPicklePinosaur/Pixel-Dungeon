#Daniel Liu
import pygame as p
import math as m
import random as r
from Collider import *

#The entity class handles the entity's stats, animation and collisions
class Entity:

    def __init__(self,spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY):
        #Entity stats
        self.spritesheet = spritesheet
        self.idleList, self.walkList = [], []
        self.spriteWidth, self.spriteHeight = spriteWidth, spriteHeight
        self.entityStats = entityStats #Load stats from spreadsheet
        self.X, self.Y = entityX, entityY #Spawn position of entity
        self.cRect = cRect
        self.speed = speed #pixel per second
        
        #Animation variables
        self.idleAniSpeed = 24 #Speed frame cycle of idle animation
        self.walkAniSpeed = 4 #Speed frame cycle of walking animation
        self.idleFrame, self.walkFrame = 0, 0
        '''
        self.hp = classStats[playerClass]['startHp']
        self.mp = classStats[playerClass]['startMp']
        self.primary = classStats[playerClass]['primary']
        self.secondary = classStats[playerClass]['secondary']
        '''
        #Player Stats
        self.hp = 100

    #ANIMATION FUNCTIONS =-=-=-=-=-=-=-=-=-=-=-=-=
    #First row  is always idle frames, second row is always walking frames
    def spritesheetCrop(self,numOfIdleFrames,numOfWalkFrames): #Take in a spritesheet and cut into sprites that are returned in a list
        spritesheetWidth, spritesheetHeight = self.spritesheet.get_width(), self.spritesheet.get_height() 
        spriteList = [[None for i in range(spritesheetWidth//self.spriteWidth)] for n in range(spritesheetHeight//self.spriteHeight)] #List to hold all cropped out sprites
        for n in range(spritesheetHeight//self.spriteHeight): #For each sprite
            for i in range(spritesheetWidth//self.spriteWidth): #Interger divison  makes sure that all cropped sprites are the same size            
                #Subsurface the spritesheet
                spriteList[n][i] = (self.spritesheet.subsurface(i*self.spriteWidth,n*self.spriteHeight,self.spriteWidth,self.spriteHeight))

        #Add sprites to walk and idle lists)
        #Put all idle momevemt frames into a list
        for i in range(numOfIdleFrames):
            self.idleList.append(spriteList[0][i])
        #Put all movement frames into a list
        for i in range(numOfWalkFrames):
            self.walkList.append(spriteList[1][i])

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

    #COLISION FUNCTIONS =-=-=-=-=-=-=-=-=-=-=-=-=
    #Check to see if the entity is colliding with anything

    '''
    @staticmethod
    #Find the collisions that are close to the entity
    def localCollision(entityRect,collLayer,elementSize): 
        direct = [(0,0),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)] #direction of adjacent cells to check for collisions
            
        #Return a list of rects that the main entity cannot collide with
        collideList = []
            
        #Round the position of the entity rect to the nearest element
        entityX, entityY = int(entityRect[0]/elementSize), int(entityRect[1]/elementSize)
        
        #Check collision for each rect next to main entity
        
        for i in range(len(direct)):
            for n in range(len(collLayer[entityY+direct[i][1]][entityX+direct[i][0]])): #For each colide object in the adjacent cell
                adjacentCell = collLayer[entityY+direct[i][1]][entityX+direct[i][0]][n]
                collideList.append(adjacentCell)
        
        for i in range(len(direct)):
            if 0 <= entityX+direct[i][0] < 16 and 0 <= entityY+direct[i][1] < 16:
                for n in range(len(collLayer[entityX+direct[i][0]][entityY+direct[i][1]])): #For each colide object in the adjacent cell
                    adjacentCell = collLayer[entityX+direct[i][0]][entityY+direct[i][1]][n]
                    collideList.append(adjacentCell)        
        return collideList
    '''
    @staticmethod
    def localCollision(entityRect,collLayer,elementSize):
        collideList = []

        for i in range(len(collLayer)):
            for n in range(len(collLayer[i])):
                if collLayer[i][n] != []:
                    for p in collLayer[i][n]:
                        collideList.append(p)

        return collideList

class Player(Entity):

    def __init__(self,spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY):
        super().__init__(spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY)

    
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

    def __init__(self,spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY):
        super().__init__(spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY)
        
        
    def kill(self):
        print('dead')


#Scale Variables
scale = 32
playerScale = 50

#Init calls
p.init()

#Set up screen

screenX, screenY = 800,600
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = int(screenX/2), int(screenY/2)


#Import test images
#Players
playerSprite = p.transform.scale(p.image.load('assets/players/martialArtist_spritesheet.png'), (5*playerScale, 2*playerScale))
enemySprite = p.transform.scale(p.image.load('assets/players/testEnemy_enemy.png'), (playerScale, playerScale))
#Map
demoMap = p.transform.scale(p.image.load('assets/maps/room_hub_hub.png'), (scale*16,scale*16))

#Create new objects
#Create player

testPlayer = Player(playerSprite,playerScale,playerScale,None,(0,0,50,50),450,0,0)
testEnemy = Enemy(enemySprite,playerScale,playerScale,None,(40,150,120,50),0,0,0)

#Crop sprite
spriteList = testPlayer.spritesheetCrop(2,5)

#Create collide objects
#Create collision data sheet for player
#rawEntityCollide = p.Rect(centerX-testPlayer.spriteWidth/2+testPlayer.cRect[0],centerY-testPlayer.spriteHeight/2+testPlayer.cRect[1],testPlayer.cRect[2],testPlayer.cRect[3])

#print(Entity.localCollision(rawEntityCollide,mapCollide,scale))
#Create collision data sheet for map objects
rawMapCollide = Collider.importCollisionMap('assets/maps/collisions/room_coll.txt',scale,16)
mapCollide = Collider.convertCollisionGrid(rawMapCollide,scale,16)

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



    #Calculate entity movement perdicter (ignore collisions)
    isWalking, moveX, moveY = testPlayer.move(seconds)

    #calculate player pos on room collision map (this pos is the top left of the IMAGE of the player
    playerX, playerY = testPlayer.X+(centerX-testPlayer.spriteWidth/2)+moveX, testPlayer.Y+(centerY-testPlayer.spriteHeight/2)+moveY
    #Update player rect (this pos is the position of the COLLISION BOX of the player)
    playerRect = p.Rect(playerX+testPlayer.cRect[0], playerY+testPlayer.cRect[1], testPlayer.cRect[2], testPlayer.cRect[3])
    #Find all collisions that are close to the player
    collideList = Entity.localCollision(playerRect,mapCollide,scale)


    #Check to see if the player collides with the collision rect
    if len(collideList) != 0:
        for i in range(len(collideList)):
            newPlayerRect = p.Rect(playerRect[0]+moveX,playerRect[1]+moveY,playerRect[2],playerRect[3])
            if newPlayerRect.colliderect(collideList[i]) == False: #If the entity does not collide with nearby collision rects, move it
                testPlayer.X += moveX
                testPlayer.Y += moveY
                break
    else:
        testPlayer.X += moveX
        testPlayer.Y += moveY

     
    
    #Update screen
    #Fill screen
    screen.fill((100,100,100))
    #shift map depending on how much the player is moving
    screen.blit(demoMap, (-testPlayer.X, -testPlayer.Y))

    p.draw.rect(screen, (255,255,0),playerRect)
    for i in range(len(collideList)):
        p.draw.rect(screen,(255,0,0),collideList[i])
        
    #Draw Players
    animatedPic = testPlayer.animate(isWalking,count) #Update player animation
    #Flip player depending on mouse poss
    if pos1 < centerX:
        pflip = p.transform.flip(animatedPic,True,False)
    else:
        pflip = animatedPic
        

    screen.blit(pflip,(centerX-pflip.get_width()/2,centerY-pflip.get_height()/2))
    
    p.display.flip()

p.quit()      
    
'''
    #Shift the map's collision objects relative to the players position if it was in the center of the screen
    for i in range(len(collideList)):
        collideList[i][0] -= testPlayer.X
        collideList[i][1] -= testPlayer.Y
        #Check to see if the player collides with the collision rect
        if p.Rect(centerX-testPlayer.spriteWidth/2,centerY-testPlayer.spriteHeight/2,testPlayer.spriteWidth,testPlayer.spriteHeight).colliderect(collideList[i]):
            testPlayer.X -= moveX
            testPlayer.Y -= moveY
    
    #Update screen
    #Fill screen
    screen.fill((100,100,100))
    #shift map depending on how much the player is moving
    screen.blit(demoMap, (-testPlayer.X, -testPlayer.Y))
    for i in range(len(collideList)):
        p.draw.rect(screen,(255,0,0),(collideList[i]))
'''

'''
#Create collide objects
#Create collision data sheet for map objects
rawMapCollide = Collider.importCollisionMap('assets/maps/collisions/room_coll.txt',scale,16)
mapCollide = Collider.convertCollisionGrid(rawMapCollide,scale,16)
#print(mapCollide)
#Create collision data sheet for player
rawEntityCollide = [p.Rect(testPlayer.X,testPlayer.Y,playerScale,playerScale)]
entityCollide = Collider.convertCollisionGrid(rawEntityCollide,scale,16)

#Compare all levels of collisions
collideList = Entity.localCollision(0,0,mapCollide,scale,5)
print(collideList)
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


    #Update screen
    screen.fill((100,100,100))

    #Update player
    playerRect = p.Rect(centerX-testPlayer.spriteWidth/2+testPlayer.cRect[0],centerY-testPlayer.spriteHeight/2+testPlayer.cRect[1],testPlayer.cRect[2],testPlayer.cRect[3])
    
    isWalking, moveX, moveY = testPlayer.move(seconds)
    #Draw Players
    animatedPic = testPlayer.animate(isWalking,count) #Update player animation
    #Flip player depending on mouse poss
    if pos1 < centerX:
        pflip = p.transform.flip(animatedPic,True,False)
    else:
        pflip = animatedPic

    #Update enemies
    enemyRect = p.Rect(testEnemy.X-testPlayer.X+centerX-testPlayer.spriteWidth/2+testEnemy.cRect[0],testEnemy.Y-testPlayer.Y+centerY-testPlayer.spriteHeight/2+testEnemy.cRect[1],testEnemy.cRect[2],testEnemy.cRect[3])
    
    
    #But if the player is going to hit a collision, undo the movement
    #Draw player and move if it isnt colliding
    #Check all surrounding collisions
    collideList = Entity.localCollision(testPlayer.X,testPlayer.Y,mapCollide,scale,3,-testPlayer.X,-testPlayer.Y)
    for i in range(len(collideList)):
        if Entity.checkCollide(playerRect,p.Rect(collideList[i])) == True:
            testPlayer.X -= moveX
            testPlayer.Y -= moveY


    #Draw screen
    #shift map depending on how much the player is moving
    screen.blit(demoMap, (-testPlayer.X, -testPlayer.Y))
    #Draw player
    screen.blit(pflip,(centerX-pflip.get_width()/2,centerY-pflip.get_height()/2))
    #Draw enemies
    screen.blit(enemySprite,(testEnemy.X-testPlayer.X+centerX-testPlayer.spriteWidth/2,testEnemy.Y-testPlayer.Y+centerY-testPlayer.spriteHeight/2))

    p.draw.rect(screen,(255,0,0),enemyRect)
    p.draw.rect(screen,(0,255,0),playerRect)
    p.draw.rect(screen, (0,255,255), rawEntityCollide[0])

    for i in range(len(collideList)):
        p.draw.rect(screen, (255,255,0), p.Rect(collideList[i]))
        
    p.display.flip()

p.quit()

'''

    
