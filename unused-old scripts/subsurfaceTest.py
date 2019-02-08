import pygame as p
import math as m

p.init()
scale = 128
playerScale = 200

#Set up screen
screen = p.display.set_mode((800,600))
weaponSurf = p.Surface((scale*2,scale*2),p.SRCALPHA)

#Import test image
bat = p.transform.scale(p.image.load('assets/items/hyperEnergyMachineGun_item.png'),(scale,scale))
gun = p.transform.scale(p.image.load('assets/items/woodenBaseballBat_item.png'),(scale,scale))
player = p.transform.scale(p.image.load('assets/players/martialArtist_player.png'),(playerScale,playerScale))


'''
def rotate(image,pos1,pos2,centerX,centerY,CORX,CORY):

    #Rotate image
    origRect = image.get_rect()
    rpic = p.transform.rotate(image,m.degrees(angle)-90)
    rRect = origRect.copy()
    rRect.center = rpic.get_rect().center
    rRect = rpic.get_rect()

    #Determine offset distance based on the new 'center' distance from real center
    distance = ((CORY)**2+(CORX)**2)**0.5
    #angle = m.atan2(CORY,CORX)
    offsetX, offsetY = distance*m.cos(angle), distance*m.sin(angle)
    return rpic, offsetX-CORX, offsetY-CORY
'''

def rotate(image,pos1,pos2,centerX,centerY,rotateX,rotateY): #Rotate image around any arbituary point
    rsurface = p.Surface((image.get_width()*2,image.get_height()*2),p.SRCALPHA) #Create a surface double the size of the image
    rsurface.fill((0,0,0,0))
    rsurface.blit(image, (image.get_width()+rotateX-image.get_width()/2,image.get_height()+rotateY-image.get_height()/2))
    
    #Determine angle of rotation depending on the position of the mouse
    angle = m.atan2(pos2-centerY,pos1-centerX)
    
    #Rotate the new surface
    rsurface = p.transform.rotate(rsurface,m.degrees(-angle))
    
    return rsurface

#Draw screen
Running = True
while Running:
    
    click = False
    for evt in p.event.get():
        #quit
        if evt.type == p.QUIT:
            Running = False

        #update mouse inputs
        pos1, pos2 = p.mouse.get_pos()
        m1, m2, m3 = p.mouse.get_pressed()

        #Determines if mouse is being clicked
        if evt.type == p.MOUSEBUTTONDOWN and m1 == 1:
            click = True

    #Refresh screen
    screen.fill((255,255,255))

    p.draw.line(screen,(255,0,0),(0,300),(800,300)) #X axis
    p.draw.line(screen,(0,0,255),(400,0),(400,600)) #Y axis
    p.draw.line(screen,(0,255,0),(pos1,pos2),(pos1,300)) #Y axis
    p.draw.line(screen,(0,0,0),(400,300),(pos1,pos2)) #hype (bullet path)
    p.draw.circle(screen,(0,255,255),(400,300),scale,1) #Weapon rotation circle

    #rpic, offsetX, offsetY = rotate(gun,pos1,pos2,400,300,40,0)
    #screen.blit(rpic,(400-offsetX-rpic.get_width()/2,300-offsetY-rpic.get_height()/2))
    rsurface = rotate(gun,pos1,pos2,400,300,30,-30)
    screen.blit(rsurface,(400-rsurface.get_width()/2,300-rsurface.get_height()/2))

    
        
    p.draw.circle(screen,(255,0,0),(400,300),1)
    p.display.flip()

quit()
