#Daniel Liu
import pygame as p
import math as m
import random as r
from pprint import *
from Entity import *
from Collider import *
from Projectile import *
        
#Scale Variables
scale = 128
playerScale = 200

#Init calls
p.init()

#Set up screen
screenX, screenY = 800,600
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = int(screenX/2), int(screenY/2)


#Import test images
#Players
playerSprite = p.transform.scale(p.image.load('assets/players/martialArtist_spritesheet.png'), (5*playerScale, 2*playerScale))
#effects
bullet = p.transform.scale(p.image.load('assets/effects/hyperEnergyDeathRay_projectile.png'), (scale, scale))


#Create new object
#Create player
testPlayer = Player(playerSprite,playerScale,playerScale,None,(20,35,10,10),200,0,0)
#Create projectiles
testBullet = Projectile(bullet,3000,2000,None,None)

#Crop sprite
testPlayer.spritesheetCrop(2,5)

#Create clock
clock = p.time.Clock()


#vars
count = 0
playerX, playerY = 400,300

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


    #Refresh screen
    screen.fill((100,100,100))


    #Update entity movement
    pIsWalking,moveX,moveY = False,0,0 #test vars

    
    #Update projectiles
    #Spawn bullet
    if click == True:
        angle = r.randint(0,359)
        testBullet.spawn(pos1,pos2,angle)

    boundRectList = [] #list to hold all bounding rects of projectiles
    #Update each projectile
    if len(testBullet.posList) > 0:
        testBullet.update(seconds)
        for i in range(len(testBullet.posList)):
            #Draw all projectiles
            bulletX, bulletY = testBullet.posList[i][0]-testBullet.imageList[i].get_width()/2, testBullet.posList[i][1]-testBullet.imageList[i].get_height()/2
            screen.blit(testBullet.imageList[i], (bulletX, bulletY))
            #Get bounding rect of projectile
            picRect = Collider.getBoundingRect(testBullet.imageList[i]) #Get bounding rect of surface
            boundRect = p.Rect(bulletX+picRect[0],bulletY+picRect[1],picRect[2],picRect[3]) #Add blit position to bounding rect

            boundRectList.append(boundRect)

            
        #Update projectile collision list
        projCollide = Collider.convertCollisionGrid(boundRectList,scale,16)

    #Check player for collisions
    playerpic = testPlayer.idleList[0]
    screen.blit(playerpic, (playerX, playerY))
    rawHitbox = Collider.getBoundingRect(playerpic)
    hitbox = p.Rect(rawHitbox[0]+playerX,rawHitbox[1]+playerY,rawHitbox[2],rawHitbox[3])

    #Convert bounding rects of projectiles into 2d list
    enemyProjCollide = Collider.convertCollisionGrid(boundRectList,scale,16)

    #Find projectile collides that are near the player
    enemyProjList = Collider.localCollision(hitbox,enemyProjCollide,scale)

    #Determine if player is colliding with any projecitles
    for i in range(len(enemyProjList)):
        if hitbox.colliderect(enemyProjList[i]) == True:
            print('ouch!')


    print(testBullet.imageList)

    
            
    p.display.flip()

p.quit()      


