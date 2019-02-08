from MapGen import *
from pygame import *

scale = 64

#Generate the map
map1 = MapGen(16,2)
MapGen.mrGenny(map1)
pprint(map1.level)

#Initate graphics
screen = display.set_mode((1600,1200))
MapGen.initGraphics()



for i in range(len(map1.level)): #For each room
    for n in range(len(map1.level[i])):

        if map1.level[i][n] != 0 and map1.level[i][n] != 2: #Draw rooms
            #Determine the type of room
            room = map1.levelMap[i][n][1]
            
            for p in MapGen.roomDict:
                for q in MapGen.roomDict[p]:
                    if map1.levelMap[i][n][1] == MapGen.roomDict[p][q]:
                        roomType = roomTypeList[p][q]
            
            screen.blit(roomType, (n*scale,i*scale))
                
        elif map1.level[i][n] == 2: #Draw hallways
            #Determine the type of room
            
            hallType = map1.levelMap[i][n][1]
            
        else: #Draw no rooms
            screen.blit(noRoom, (n*scale,i*scale))


display.flip()
time.wait(10000)
quit()
