#Daniel Liu
import pygame as p
import math as m
import random as r
import Setup
from pprint import *
from XLSX import *
from Projectile import *

class Weapon:

    def __init__(self,name,image,projectile,baseAtkRate,centerX,centerY,muzzlePos):
        self.name = name #Used only for creating object via dict comp
        self.image = p.transform.scale(p.image.load(image),(Setup.scale,Setup.scale)) #load weapon sprite
        self.projectile = projectile #weapon projectiles (these include sword slashes etc.)(may be list)
        self.baseAtkRate = baseAtkRate  #The cooldown before the next attack
        self.muzzlePos = muzzlePos #The distance from the gun image's center to the muzzle (used as the spawn location of the projectiles)

        #Visual aspect of weapon
        self.centerX, self.centerY = centerX, centerY #Location of weapon handle relative to the center of the image

    '''
    @property
    #Update weapon stas based on player's perks
    def weaponMod(self,playerDmg,playerFireRate,playerCritChance):
        self.dmg = self.baseDmg + playerDmg
        self.fireRate = self.baseFireRate + playerFireRate
        self.critChance = self.baseCritChance + playerCritChance
    '''

    #Weapon Behavior/Graphics
    def rotate(self,pos1,pos2,centerX,centerY,rotateX,rotateY,offsetAngle=0):
        rsurface = p.Surface((self.image.get_width()*2,self.image.get_height()*2),p.SRCALPHA) #Create a surface double the size of the image
        rsurface.fill((0,0,0,0))
        rsurface.blit(self.image, (self.image.get_width()/2+rotateX,self.image.get_height()/2+rotateY))
        
        #Determine angle of rotation depending on the position of the mouse
        angle = m.atan2(pos2-centerY,pos1-centerX)

        #Rotate and Flip the image based on mouse position
        if pos1 <= centerX:
            rsurface = p.transform.flip(p.transform.rotate(rsurface,m.degrees(angle)+offsetAngle), False, True)
        else:
            rsurface = p.transform.rotate(rsurface,m.degrees(-angle)+offsetAngle)
        
        return rsurface
        

#Subclass of weapon
class RangeWeapon(Weapon):
            
    def __init__(self,name,image,projectile,baseAtkRate,centerX,centerY,muzzlePos,spread,shots,clipSize,reloadTime,rarity,autoFire=False):
        super().__init__(name,image,projectile,baseAtkRate,centerX,centerY,muzzlePos) #Call on Weapon class' init method
        self.spread = spread  #The range of inaccuracy the gun has (in angles)
        self.shots = shots #Number of bullets shot each time the weapon fires
        self.clipSize = clipSize  #Amount of bullets weapon can shoot before reloading
        self.clipCount = clipSize  #Amount of bullets left in mag
        self.reloadTime = reloadTime  #Amount of time it takes to reload in seconds
        self.rarity = rarity
        self.autoFire = autoFire

class MeleeWeapon(Weapon):
    
    def __init__(self,name,image,projectile,baseAtkRate,centerX,centerY,muzzlePos,swingAngle,swingSpeed,rarity):
        super().__init__(name,image,projectile,baseAtkRate,centerX,centerY,muzzlePos)
        #Melee swing vars
        self.swingAngle = swingAngle
        self.swingSpeed = swingSpeed
        self.curSwingAngle = 0
        self.swingMode = 0 #Swing modes - 0:None, 1:Down, 2:Up, 3:reset
        self.rarity = rarity
    
    
    def meleeSwing(self,pos1,pos2,centerX,centerY):

        #Start swing if the function is called
        if self.swingMode == 0:
            self.swingMode = 1

        #Start downward swing
        if self.swingMode == 1:
            self.curSwingAngle += self.swingSpeed
            
        #Reverse swing if the swing angle is greater than the max swingangle
        if self.curSwingAngle >= self.swingAngle:
            self.swingMode = 2
            
        #Start upward swing
        if self.swingMode == 2:
            self.curSwingAngle -= self.swingSpeed*0.8

        #End swing
        if self.curSwingAngle < 0:
            self.swingMode = 3
            self.curSwingAngle = 0

        #Rotate the weapon depending on the mouse pos and current swing offset angle
        rsurface = self.rotate(pos1,pos2,centerX,centerY,self.centerX,self.centerY,-self.curSwingAngle)
        return rsurface
        
''' 
#Scale Variables
scale = 128
playerScale = 200

#Init calls
p.init()

#Set up screen
screenX, screenY = Setup.screenX, Setup.screenY
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = Setup.centerX, Setup.centerY


#Import test images
#Players
player = p.transform.scale(p.image.load('assets/entities/martialArtist_player.png'), (playerScale, playerScale))
muzzleFlash = p.transform.scale(p.image.load('assets/effects/muzzleFlash_effect.png'), (scale, scale))
'''
'''
#Weapons
gun = p.transform.scale(p.image.load('assets/items/hyperEnergyMachineGun_item.png'), (scale, scale))
bat = p.transform.scale(p.image.load('assets/items/woodenBaseballBat_item.png'), (scale, scale))
navBat = p.transform.scale(p.image.load('assets/items/navBat_item.png'), (scale, scale))
spear = p.transform.scale(p.image.load('assets/items/spear_item.png'), (scale, scale))
bow = p.transform.scale(p.image.load('assets/items/fireyBow_item.png'), (scale, scale))
#Effects (such as projectiles)
bullet = p.transform.scale(p.image.load('assets/effects/hyperEnergyDeathRay_projectile.png'), (scale, scale))
slash = p.transform.scale(p.image.load('assets/effects/testSlash_projectile.png'), (scale, scale))
thrust= p.transform.scale(p.image.load('assets/effects/thrust_projectile.png'), (scale, scale))
arrow = p.transform.scale(p.image.load('assets/effects/fireArrow_projectile.png'), (scale, scale))

#Create new objects
#Create new projectiles
testBullet = Projectile(bullet,300,2000,None,None)
testSlash = Projectile(slash,40,150,None,None)
testThrust = Projectile(thrust,100,500,None,None)
testArrow = Projectile(arrow,400,1200,None,None)

# Create new test weapons
HEMG_weapon = RangeWeapon(gun,testBullet,None,75,None,0,0,70,7,1,60,2000,True)
bat_weapon = MeleeWeapon(bat,testSlash,None,75,None,30,-25,100,100,9)
navBat_weapon = MeleeWeapon(navBat,testSlash,None,75,None,30,-25,100,160,18)
spear_weapon = RangeWeapon(spear,testThrust,None,100,None,20,0,60,4,1,None,0,True)
fireBow_weapon = RangeWeapon(bow,testArrow,None,100,None,0,0,0,1,1,1,500,True)
'''

'''
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

#Create clock
clock = p.time.Clock()

#vars
curWeapon = meleeObjects['baseballBat_weapon']

reloading = False
firing = False
shoot = False
swing = False

#Custom events
RELOAD = p.USEREVENT + 1
FIRING = p.USEREVENT + 2

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
                projectileObjects[curWeapon.projectile].spawn(centerX+curWeapon.muzzlePos*m.cos(angle), centerY+curWeapon.muzzlePos*m.sin(angle), angle)

            

    #Update screen
    screen.fill((100, 100, 100))

    #Draw refrence lines
    p.draw.line(screen, (255, 0, 0), (0, 300), (800, 300))  #X axis
    p.draw.line(screen, (0, 0, 255), (400, 0), (400, 600))  #Y axis
    p.draw.line(screen, (0, 255, 0), (pos1, pos2), (pos1, 300))  #Y axis
    p.draw.circle(screen, (0, 255, 255), (400, 300), scale, 1)  #Weapon rotation circle
    p.draw.line(screen, (0, 0, 0), (400, 300), (pos1, pos2))  #hype (bullet path)

    if pos1 <= 400:  #Flip player based on mouse position
        screen.blit(p.transform.flip(player, True, False),(400-playerScale/2, 300-playerScale/2-50))
    else:
        screen.blit(player, (400-playerScale/2, 300-playerScale/2-50))


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
                projectileObjects[curWeapon.projectile].spawn(centerX+curWeapon.muzzlePos*m.cos(angle), centerY+curWeapon.muzzlePos*m.sin(angle), angle)
                #Each time a projectile is spawned, reduce number of ammo left
                if curWeapon.clipCount != None:
                    curWeapon.clipCount -= 1
                    if curWeapon.clipCount <= 0: #Dont shoot all shots if clip runs out
                        break
                
            #Draw muzzle flash
            rpic = p.transform.rotate(muzzleFlash, m.degrees(-angle))
            screen.blit(rpic, (centerX+(curWeapon.muzzlePos)*m.cos(angle)-rpic.get_width()/2, centerY+(curWeapon.muzzlePos)*m.sin(angle)-rpic.get_height()/2))


            shoot = False

        #Update each projectile on map according to update rate
        if len(projectileObjects[curWeapon.projectile].posList) > 0:
            projectileObjects[curWeapon.projectile].update(seconds)  #Update position of all projectiles on map
            #Visually update the position of all projectiles on map
            for i in range(len(projectileObjects[curWeapon.projectile].posList)):
                screen.blit(projectileObjects[curWeapon.projectile].imageList[i], (projectileObjects[curWeapon.projectile].posList[i][0]-projectileObjects[curWeapon.projectile].imageList[i].get_width()/2, projectileObjects[curWeapon.projectile].posList[i][1]-projectileObjects[curWeapon.projectile].imageList[i].get_height()/2))

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

        #Update each projectile on map according to update rate
        if len(projectileObjects[curWeapon.projectile].posList) > 0:
            projectileObjects[curWeapon.projectile].update(seconds)  #Update position of all projectiles on map
            #Visually update the position of all projectiles on map
            for i in range(len(projectileObjects[curWeapon.projectile].posList)):
                screen.blit(projectileObjects[curWeapon.projectile].imageList[i], (projectileObjects[curWeapon.projectile].posList[i][0]-projectileObjects[curWeapon.projectile].imageList[i].get_width()/2, projectileObjects[curWeapon.projectile].posList[i][1]-projectileObjects[curWeapon.projectile].imageList[i].get_height()/2))

    p.display.flip()

p.quit()

'''
