from pprint import *
import pygame as p
import random as r

'''
a blank space is indicated with a 0
a room is indicated with a 1
a hallway is inicated with a 2
spawn point is indicated with a 5
exit point is indicated with a 6
a chest room is indicated with a 7
a shop room is indicated with an 8

Generation Rules
-Every room needs to be attached to at least one hallway
-No rooms may be attached to another room directly
-The spawn room must have only one exit

Notes:
-specials are the spawn room(5), chest rooms, exit rooms(6) and boss rooms

Number of exits in a room are indicated by a 4 element list (starting from the right side and going counterclockwise), 1 indicates exit, 0 indicates nothing
'''

class MapGen:

  #Room Types
  hallwayDict = {'hallway':{'RL':[1,0,1,0],'UD':[0,1,0,1]}}
  roomDict = {'cap':{'R':[1,0,0,0],'U':[0,1,0,0],'L':[0,0,1,0],'D':[0,0,0,1]},'funnel':{'RL':[1,0,1,0],'UD':[0,1,0,1]},'L':{'RU':[1,1,0,0],'UL':[0,1,1,0],'LD':[0,0,1,1],'DR':[1,0,0,1]},'T':{'R':[0,1,1,1],'U':[1,0,1,1],'L':[1,1,0,1],'D':[1,1,1,0]}, 'hub':{'hub':[1,1,1,1]}}

  #Graphical representation of each room type
  roomTypeList = {}
  hallwayTypeList = {}
  

  
  def __init__(self, mapSize, complexity): #Set instance variables
    self.mapSize = mapSize
    self.complexity = complexity
    self.level = [[0 for i in range(mapSize)] for i in range(mapSize)] #Maps out the position of rooms and hallways
    self.levelMap = [[[] for i in range(mapSize)] for i in range(mapSize)] #Maps out the type of room or hallway
  
  @classmethod
  def initGraphics(self): #Loads all room types (to decrease some lag)
    #Load rooms
    for i in MapGen.roomDict:
      MapGen.roomTypeList[i] = {}
      for n in MapGen.roomDict[i]:
          MapGen.roomTypeList[i][n] = [transform.scale(image.load("assets/maps/room_"+i+"_"+n+".png"),(scale,scale)),map1.roomDict[i][n]]
    #Load hallways
    hallway_UD = transform.scale(image.load("assets/maps/hallway_UD.png"),(scale,scale))
    hallway_RL = transform.scale(image.load("assets/maps/hallway_RL.png"),(scale,scale))
    #Load NoRoom
    noRoom = transform.scale(image.load("assets/maps/noRoom.png"),(scale,scale))

    
  def mrGenny(self): #mrGenny builds the map and checks that it meets the requirements
    while True:
      self.level = [[0 for i in range(self.mapSize)] for i in range(self.mapSize)] #Clear map
      #Plot a random even coordinate on map as the spawn point
      startX, startY = r.randint(1,(self.mapSize-1)//2-1)*2, r.randint(1,(self.mapSize-1)//2-1)*2
      self.level[startY][startX] = 5
      
      #Queue for rooms that have a chance of gaining another exit
      newRoomList = [(startX,startY)]
    
      while len(newRoomList) != 0: #If there are no more new rooms, end the program
        
        #Update current room position
        roomX, roomY = newRoomList[0][0], newRoomList[0][1]
        
        #Add new room
        #Choose a random direction to make the room branch off in
        directChoices = [(1,0),(0,1),(-1,0),(0,-1)]
        
        #Remove the possibility for the path leading to the room to be chosen
        for w in range(0,4):
          if self.level[roomY+directChoices[w][1]][roomX+directChoices[w][0]] != 0:
            del directChoices[directChoices.index((directChoices[w][1],directChoices[w][0]))]
            break
        
        #Pick a random amount of exits the room can have
        #Chance for room to have no more exits
        capChance = r.randint(0,self.mapSize//2) #Chance that the path ends there scales with the size of the map
        
        if capChance == self.mapSize//1.5:
          numOfExits = 0
          roomX, roomY = -1, -1
        else:
          numOfExits = 1
        
        #Give a chance for the current room to be deleted from queue (if it is, that means thats how many exits it has, if not it has a chance to get more)
        newRoomChance = r.randint(0,10*self.complexity) #VERY IMPORTANT IN STRUCTURE OF DUNGEON
        if newRoomChance < 10:
          del newRoomList[newRoomList.index((roomX,roomY))]
        
        for y in range(numOfExits):
          direct = r.choice(directChoices) #choose direction
      
          if -1 < roomY+direct[1] < self.mapSize-1 and -1 < roomX+direct[0] < self.mapSize-1 and -1 < roomY+direct[1]*2 < self.mapSize-1 and -1 < roomX+direct[0]*2 < self.mapSize-1: #Check that the room is not next to a border
            if self.level[roomY+direct[1]][roomX+direct[0]] == 0 and self.level[roomY+direct[1]*2][roomX+direct[0]*2] == 0: #Check in a 2x1 rect in from of room that the space is avaliable
              self.level[roomY+direct[1]][roomX+direct[0]] = 2
              self.level[roomY+direct[1]*2][roomX+direct[0]*2] = 1
              
              #Update selected room position
              roomX += direct[0]*2
              roomY += direct[1]*2
              
              #Add new room to queue list
              newRoomList.append((roomX,roomY))
      
      
      #Check that the room meets the requirements
      #Count the number of rooms
      roomCount = 0
      spawnCount = 0
      exitCount = 0
      for i in range(len(self.level)):
        for n in range(len(self.level[i])):
          if self.level[i][n] == 1:
            roomCount += 1
          elif self.level[i][n] == 5:
            spawnCount += 1
     
      if 5 < roomCount < self.mapSize*2 and spawnCount == 1: #If the generated dungeon matches the requirements, stop generating
        break
      else:
        print('regenerating')
        
  def mrClassy(self): 
    #Map the room Types based on the # of exits
    #Scan the four directions around the room for other rooms/hallways
    directChoices = [(1,0),(0,-1),(-1,0),(0,1)]
    for i in range(len(self.level)): #For each room in map
      for n in range(len(self.level[i])):
        directKey = []
        for direct in directChoices:
          if -1 < i+direct[1] < self.mapSize-1 and -1 < n+direct[0] < self.mapSize-1: #Check that the room is not next to a border
            if self.level[i+direct[1]][n+direct[0]] != 0: #If the room adjacent to the current room isnt empty, assume it's a room and the rooms are connected
              directKey.append(1)
            elif self.level[i+direct[1]][n+direct[0]] == 0: #Otherwise, there is no path leading to that direction
              directKey.append(0) 
          else: #If a border is detected, there is no exit in that direction
            directKey.append(0)

        #Determine the type of room (hallway, chest room etc)
        if self.level[i][n] == 0: #If there is no room, we don't care how many exits it has
          self.levelMap[i][n] = 0
        else:
          self.levelMap[i][n] = {self.level[i][n] : directKey}
    '''
    def mrMapper(self): #MrMapper determines which room image corresponds to which room, Requires that initGraphics has been called
      #MrMapper also builds on the levelMap
      for i in range(len(self.levelMap)): #For each room on map
          for n in range(len(self.levelMap[n])):
                
              for p in roomDict: #Search room dict for matching type of rooms
                  for q in roomDict[p]:
                      if roo
    '''
    
     

#=-=-=-=-=-=-=-=-=-=-=-=-=-=
myLevel = MapGen(16,3.2) #Create level map

'''
myLevel.mrGenny() #Generate the room layout

pprint(myLevel.level)

myLevel.mrClassy() #Determine the type of room depending on the amount of exits has

pprint(myLevel.levelMap)
'''
myLevel.initGraphics()

print(myLevel.hallwayDict)
