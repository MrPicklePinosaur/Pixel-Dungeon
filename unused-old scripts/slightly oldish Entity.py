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

    entityPosList = []
    
    def __init__(self,spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY):
        super().__init__(spritesheet,spriteWidth,spriteHeight,entityStats,cRect,speed,entityX,entityY)
        

    def spawn(spawnX,spawnY):
        entityPosList.append((spawnX, spawnY))

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


#Import test images
#Players
playerSprite = p.transform.scale(p.image.load('assets/players/martialArtist_spritesheet.png'), (5*playerScale, 2*playerScale))
enemySprite = p.transform.scale(p.image.load('assets/players/testEnemy_spritesheet.png'), (playerScale, 2*playerScale))
#Map
demoMap = p.transform.scale(p.image.load('assets/maps/room_hub_hub.png'), (scale*16,scale*16))


#Create new objects
#Create player
testPlayer = Player(playerSprite,playerScale,playerScale,None,(20,35,10,10),200,0,0)
#Create entities
testEnemy = Enemy(enemySprite,playerScale,playerScale,None,(20,30,10,10),0,100,10)

#Crop sprite
testPlayer.spritesheetCrop(2,5)
testEnemy.spritesheetCrop(1,1)


#Create collide objects
#Create collision data sheet for map objects
rawMapCollide = Collider.importCollisionMap('assets/maps/collisions/room_coll.txt',scale,16) #Import raw collisions data
mapCollide = Collider.convertCollisionGrid(rawMapCollide,scale,16) #Covert collision data into collision rect objects

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
    pIsWalking, moveX, moveY = testPlayer.move(seconds)

    #Calculate player pos on room collision map (this pos is the top left of the IMAGE of the player
    playerX, playerY = testPlayer.X+(centerX-testPlayer.spriteWidth/2), testPlayer.Y+(centerY-testPlayer.spriteHeight/2)
    #Update player rect (this pos is the position of the movement COLLISION BOX of the player)
    movePlayerRect = p.Rect(playerX+testPlayer.cRect[0], playerY+testPlayer.cRect[1], testPlayer.cRect[2], testPlayer.cRect[3])
    #Find all collisions that are close to the player
    collideList = Collider.localCollision(movePlayerRect,mapCollide,scale)

    #Check to see if the player collides with anything near it
    for i in range(len(collideList)):
        newPlayerRect = p.Rect(movePlayerRect[0]+moveX,movePlayerRect[1]+moveY,movePlayerRect[2],movePlayerRect[3])
        if newPlayerRect.colliderect(collideList[i]) == True: #If the entity does not collide with nearby collision rects, move it
            break
    else: #Move player if the predicted player movement doesnt collide 
        testPlayer.X += moveX
        testPlayer.Y += moveY


    #Entity movement


    
    #Update screen
    #Fill screen
    screen.fill((100,100,100))
    #Shift map depending on how much the player is moving
    screen.blit(demoMap, (-testPlayer.X, -testPlayer.Y))

    #Draw Entites
    #Draw player
    animatedPic = testPlayer.animate(pIsWalking,count) #Update player animation
    #Flip player depending on mouse pos
    if pos1 < centerX:
        pflip = p.transform.flip(animatedPic,True,False)
    else:
        pflip = animatedPic

    screen.blit(pflip,(centerX-pflip.get_width()/2,centerY-pflip.get_height()/2)) #Draw Player in center of the screen

    p.draw.rect(screen, (255,255,0),movePlayerRect)

    for i in range(len(collideList)):
        p.draw.rect(screen,(255,0,0),collideList[i])
        
    p.draw.rect(screen, (0,255,255), p.Rect(centerX-pflip.get_width()/2+testPlayer.cRect[0],centerY-pflip.get_height()/2+testPlayer.cRect[1],testPlayer.cRect[2],testPlayer.cRect[3]))
                                            
    
    p.display.flip()

p.quit()      
'''
