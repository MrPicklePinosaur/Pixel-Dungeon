import pygame as p
import math as m

p.init()
scale = 128
playerScale = 200

class Weapon:
    
    def __init__(self,image,projectile,baseDmg,baseFireRate,baseCritChance,clipSize):
        self.image = image #weapon sprite
        self.projectile = projectile #weapon projectiles (these include sword slashes etc.)(may be list)
        self.baseDmg = baseDmg #damage before player dmg modifier
        self.baseFireRate = baseFireRate #damage before player fire rate modifier
        self.baseCritChance = baseCritChance #crit chance (%) before player modifier
        self.clipSize = clipSize

    def weaponMod(self,playerDmg,playerFireRate,playerCritChance):
        self.dmg = self.baseDmg + playerDmg
        self.fireRate = self.baseFireRate + playerFireRate
        self.critChance = self.baseCritChance + playerCritChance
        
    #Weapon Behavior/Graphics
    
    @staticmethod
    def rotate(image,angle):
        origRect = image.get_rect()
        rotateImage = p.transform.rotate(image,angle)
        rotatedRect = origRect.copy()
        rotatedRect.center = rotateImage.get_rect().center
        return rotateImage

        

    def weaponRotate(self,pos1,pos2,centerX,centerY,angle=None):
        #Weapon is on the center of the screen
        #Rotate gun to mouse pos
        if angle == None: #If there is no input angle, determine an angle based on mouse pos
            if (((pos1-centerX)**2+(pos2-centerY)**2)**0.5) != 0:
                angle = m.degrees(m.asin((pos2-centerY)/(((pos1-centerX)**2+(pos2-centerY)**2))**0.5)) #Find rotating angle
            else:
                angle = 0
        else:
            angle = angle 
        
        #Rotate image and flip image if the mouse is on other side of screen
        if pos1 <= centerX:
            rotatedWeapon = p.transform.flip(Weapon.rotate(self.image,-angle),True,False)
        else:
            rotatedWeapon = Weapon.rotate(self.image,-angle)

        return rotatedWeapon

    
class MeleeWeapon(Weapon):

    def meleeSwing(self,pos1,pos2,centerX,centerY,swingMode,currentAngle,swingAngle=90):
        
        #Reverse swing direction if the whole downward swing is completed
        if currentAngle >= swingAngle: 
            swingMode = 'up'

        #End swing if the melee weapon has been swung down and brough back to it's original pos
        elif currentAngle < 0:
            swingMode = 'none'
            
        #Swing weapon while animating is not complete
        if swingMode == 'down':
            currentAngle += 1.5

        #Swing weapon back to it's original position after initial swing
        elif swingMode == 'up':
            currentAngle -= 3

        angle = m.degrees(m.asin((pos2-centerY)/(((pos1-centerX)**2+(pos2-centerY)**2))**0.5)) + currentAngle
        rpic = self.weaponRotate(pos1,pos2,400,300,angle)
        return swingMode, currentAngle, rpic


class Projectile:

    def __init__(self, image, projectileRange, speed, dmg, pierceAmount):
        self.image = image
        self.range = projectileRange
        self.speed = speed
        self.dmg = dmg
        self.pierceAmount = pierceAmount
        

    def update(self,angle,PX,PY): #Moves projectile
        PX += speed*cos(angle)
        PY += speed*sin(angle)
        return PX, PY

        

#Set up screen
screen = p.display.set_mode((800,600))

#Import test image
gun = p.transform.scale(p.image.load('assets/items/hyperEnergyMachineGun_item.png'),(scale,scale))
bat = p.transform.scale(p.image.load('assets/items/woodenBaseballBat_item.png'),(scale,scale))
player = p.transform.scale(p.image.load('assets/players/martialArtist_player.png'),(playerScale,playerScale))



#Create new test weapons
HEMG_weapon = Weapon(gun,None,None,None,None,None)
nav_weapon = MeleeWeapon(bat,None,None,None,None,None)

#vars
curWeapon = HEMG_weapon
swingMode = 'none'

#Active loop
running = True
while running:
    
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
    p.draw.circle(screen,(0,255,255),(400,300),scale,1) #Weapon rotation circle
    p.draw.line(screen,(0,0,0),(400,300),(pos1,pos2)) #hype (bullet path)
    
    if pos1 <= 400: #Flip player based on mouse position
        screen.blit(p.transform.flip(player,True,False),(400-playerScale/2,300-playerScale/2-50))
    else:
        screen.blit(player,(400-playerScale/2,300-playerScale/2-50))


    #Swing melee weapon
    if click == True and isinstance(curWeapon,MeleeWeapon) == True and swingMode == 'none':
        swingMode,currentAngle = 'down',0

    if swingMode != 'none':
        swingMode,currentAngle,rpic = curWeapon.meleeSwing(pos1,pos2,400,300,swingMode,currentAngle,90)
        screen.blit(rpic,(400-rpic.get_width()//2,300-rpic.get_height()//2))


    #Draw weapon
    if swingMode == 'none':
        rpic=curWeapon.weaponRotate(pos1,pos2,400,300)
        screen.blit(rpic,(400-rpic.get_width()//2,300-rpic.get_height()//2)) #Rotate weapon
        
        
    p.display.flip()

p.quit()

