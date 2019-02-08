#Daniel Liu
import pygame as p
import math as m
import Setup 

class Projectile:

    def __init__(self,name,image,projectileRange,speed,dmg): #Projectile info
        self.name = name
        self.image = p.transform.scale(p.image.load(image),(Setup.scale,Setup.scale))
        self.range = projectileRange #Total distance the projectile can travelled before 'dying'
        self.speed = speed #Travel speed of projectile in pixels per second
        self.dmg = dmg
                
        #Orientation of bullets - List of all bullets and their positional information
        self.imageList = [] #Rotated version of each projectile
        self.posList = [] #Current position of each projectile
        self.angleList = [] #The angle relative to center of each active projectile
        self.distList = [] #Distance each projectile has travelled


    def spawn(self,startX,startY,angle): #Create a new projectile with the same stats as the class
        self.imageList.append(p.transform.rotate(self.image, (m.degrees(-angle)))) #Rotate image based on firing angle
        self.posList.append((startX,startY)) #Set start point of projectile
        self.angleList.append(angle)
        self.distList.append(self.range) 

    def kill(self,killList): #Delete projectiles
        #Use list comprehension to create a new list with only the projectiles that shuldnt be deleted
        self.imageList[:] = [self.imageList[i] for i in range(len(self.imageList)) if i not in killList]
        self.posList[:] = [self.posList[i] for i in range(len(self.posList)) if i not in killList]
        self.angleList[:] = [self.angleList[i] for i in range(len(self.angleList)) if i not in killList]
        self.distList[:] = [self.distList[i] for i in range(len(self.distList)) if i not in killList]

    def update(self,currentTD): #Moves each active projectile

        #Check to see if any projectiles needs to be 'killed'
        removeList = [i for i in range(len(self.distList)) if self.distList[i] <= 0] #find the index of all the projectiles that need to be killed
        if len(removeList) != 0:
            self.kill(removeList)
        
        for i in range(len(self.posList)):
            offsetX, offsetY = self.posList[i][0]+self.speed*currentTD*m.cos(self.angleList[i]),self.posList[i][1]+self.speed*currentTD*m.sin(self.angleList[i])
            self.posList[i] = (offsetX,offsetY)
            self.distList[i] -= self.speed*currentTD #Update distance the projectile has travelled
            
        return self.posList

'''
#Scale Variables
scale = 128

#Init calls
p.init()

#Set up screen
screenX, screenY = 800,600
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = int(screenX/2), int(screenY/2)

#Import assets
#Import test image
gun = p.transform.scale(p.image.load('assets/items/hyperEnergyMachineGun_item.png'),(scale,scale))
bullet = p.transform.scale(p.image.load('assets/effects/hyperEnergyDeathRay_projectile.png'),(scale,scale))

#Create new objects
#Create new bullet type
testBullet = Projectile(bullet,400,40,None,None)

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
        if evt.type == p.MOUSEBUTTONDOWN and m1 == 1:
            click = True
            
    #Update screen
    screen.fill((255,255,255))
    
    #Draw refrence lines
    p.draw.line(screen,(255,0,0),(0,300),(800,300)) #X axis
    p.draw.line(screen,(0,0,255),(400,0),(400,600)) #Y axis
    p.draw.line(screen,(0,255,0),(pos1,pos2),(pos1,300)) #Y axis
    p.draw.line(screen,(0,0,0),(centerX,centerY),(pos1,pos2)) #hype (bullet path)
            
    if click == True:
        #Spawn bullet
        angle = m.atan2(pos2-centerY,pos1-centerX)
        #Center the bullet
        tempMesh = p.transform.rotate(testBullet.image, (m.degrees(-angle)))
        testBullet.spawn(centerX-tempMesh.get_width()/2,centerY-tempMesh.get_height()/2,angle)

    #Update each projectile on map
    if len(testBullet.posList) > 0:
        testBullet.update(seconds) #Update position of all projectiles on map
        for i in range(len(testBullet.posList)): #Visually update the position of all projectiles on map
            screen.blit(testBullet.imageList[i],(testBullet.posList[i][0],testBullet.posList[i][1]))


    p.display.flip()

p.quit()

'''

    
