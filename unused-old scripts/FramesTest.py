import pygame as p
import math as m

p.init()
playerScale = 200

#Set up screen
screen = p.display.set_mode((800,600))

#Import test images
player = p.transform.scale(p.image.load('assets/players/martialArtist_player.png'),(playerScale,playerScale))

#Move function
def move(speed,currentTD,playerX,playerY):
    POFFX, POFFY = 0, 0 #Player direction variables

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
        playerX += speed*currentTD*m.cos(angle)
        playerY += speed*currentTD*m.sin(angle)
        isWalking = True
    else:
        isWalking = False

    return isWalking, playerX, playerY

#variables
playerX, playerY = 400, 300
elapsed = 0
#Draw screen
screen.fill((255,255,255))
screen.blit(player,(playerX,playerY))

#Setup clock
clock = p.time.Clock()

#Active loop
running = True
while running:
    
    #Time stepping
    #Update timedelta to maintain constant movement in space and time
    timedelta = clock.tick(60)
    print(timedelta)
    seconds = timedelta/1000 #Convert from milliseconds to seconds
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


    #Move character
    isWalking,playerX,playerY = move(1000,seconds,playerX,playerY)
    if isWalking == True:
        screen.fill((255,255,255))
        screen.blit(player,(playerX,playerY))






 
    p.display.flip()

p.quit()

