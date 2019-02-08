#Daniel Liu
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
-specials are the spawn room(5), chest rooms(7), exit rooms(6) and boss rooms

Number of exits in a room are indicated by a 4 element list (starting from the right side and going counterclockwise [R,U,L,D]), 1 indicates exit, 0 indicates nothing
'''

class MapGen:
      
  #Room Types
  roomDict = {'cap':{'R':[1,0,0,0],'U':[0,1,0,0],'L':[0,0,1,0],'D':[0,0,0,1]},'funnel':{'RL':[1,0,1,0],'UD':[0,1,0,1]},'L':{'RU':[1,1,0,0],'UL':[0,1,1,0],'LD':[0,0,1,1],'DR':[1,0,0,1]},'T':{'R':[0,1,1,1],'U':[1,0,1,1],'L':[1,1,0,1],'D':[1,1,1,0]}, 'hub':{'hub':[1,1,1,1]}}
  hallwayDict = {'hallway':{'RL':[1,0,1,0],'UD':[0,1,0,1]}}
  otherDict = {'none':{'none':[0,0,0,0]}}

  #Layout Types
  #roomLayoutDict - form {layoutname:[numOfLayoutVariations,[listOfLayoutCollisions(unloaded)],[listOfVariationImages(unloaded)]]}
  roomLayoutDict = {'boxes':[8,[],[]],'holes':[6,[],[]],'misc':[3,[],[]]}
  specialRoomLayoutDict = {'spawn':[1,[],[]],'exit':[1,[],[]],'chest':[1,[],[]]}

  #Objects
  #Doors
  doorDict = {'R':[15,6,1,5],'U':[6,0,4,2],'L':[0,6,1,5],'D':[6,15,4,2]} #Amount of elements each door takes up
  
  def __init__(self, mapSize, complexity): #Set instance variables
    self.mapSize = mapSize
    self.complexity = complexity
    self.level = [[0 for i in range(mapSize)] for i in range(mapSize)] #Maps out the position of rooms and hallways
    self.levelMap = [[[] for i in range(mapSize)] for i in range(mapSize)] #Maps out the type of room or hallway
    self.layoutMap = [[[] for i in range(mapSize)] for i in range(mapSize)] #keeps track of the room layout of each room
    self.roomCollide = [[None for i in range(mapSize)] for i in range(mapSize)] #Keeps track of the collisions for each room (including the room Layout)
    self.mrCollisionData = [[None for n in range(mapSize)] for i in range(mapSize)] #master list that holds all collision data
    self.entities = [[[] for n in range(mapSize)] for i in range(mapSize)] #Stores the entities in the room
    self.progress = [[None for n in range(mapSize)] for i in range(mapSize)] #Keeps track which rooms has been cleared
    self.items = [[None for n in range(mapSize)] for i in range(mapSize)] #Keeps track of all the dropped weapons on the ground
        
    #Objects
    self.doorPosList = [[None for n in range(mapSize)] for i in range(mapSize)] #All door objects on map
    self.chestPosList = [] #All chest objects on map

  #Utility functions
  @staticmethod
  #Extract map collision data from file
  def importCollisionMap(rawMapData):
      #Collision: 0 - None, 1 - Standard Collision, 2 - Entity-only Collision, 3 - Interactable, 4 - Enemy spawn
      #Read from file to extrace collisions
      rawData = open(rawMapData).readlines()
      #Create a 2d array to get the position of the map rect
      rawCollideList = [i.replace('\n','').split(' ') for i in rawData] #clean up file 

      return rawCollideList
    
  @staticmethod
  #Creates a new collision grid with two pre-exisiting ones, the topLayer over-rides the base
  def mergeCollideLayers(baseLayer,topLayer):
      #Create copy of base layer
      newLayer = [[None for i in range(len(baseLayer[n]))] for n in range(len(baseLayer))]
      
      for i in range(len(topLayer)): #Iterate through top layer
          for n in range(len(topLayer[i])):
              #Treat empty areas as transparent (ex, an element with no collision object is transparent)
              if int(topLayer[i][n]) != 0:
                  newLayer[i][n] = topLayer[i][n]
              elif int(topLayer[i][n]) == 0:
                  newLayer[i][n] = baseLayer[i][n]
                  
      return newLayer

  #Init, used so there wont be super long wait times when starting the game
  @classmethod
  def initGraphics(cls,roomSize):
    #Loads images (seperate function to reduce lag)
    #=-=-=-=-= Rooms =-=-=-=-=
    #Load all rooms types
    for i in cls.roomDict: #Replace each value in roomDict with the roomType AND the image
      for n in cls.roomDict[i]:
        scalepic = p.transform.scale(p.image.load("assets/newMaps/room_"+i+"_"+n+".png"),(roomSize,roomSize)) #scale image
        rawCollideList = "assets/newMaps/collisions/room_"+i+"_"+n+".txt"
        cls.roomDict[i][n] = [cls.roomDict[i][n], rawCollideList, scalepic]
    #Load all hallway types
    for i in cls.hallwayDict: #Replace each value in hallWayDict with the hallWayType AND the image
      for n in cls.hallwayDict[i]:
        scalepic = p.transform.scale(p.image.load("assets/newMaps/hallway_"+i+"_"+n+".png"),(roomSize,roomSize))
        rawCollideList = "assets/newMaps/collisions/hallway_"+i+"_"+n+".txt"
        cls.hallwayDict[i][n] = [cls.hallwayDict[i][n], rawCollideList, scalepic]
    #Load empty element
    scalepic = p.transform.scale(p.image.load("assets/newMaps/room_None.png"),(roomSize,roomSize))
    rawCollideList = "assets/newMaps/collisions/room_None.txt"
    cls.otherDict['none']['none'] = [cls.otherDict['none']['none'], rawCollideList, scalepic]
    
    #=-=-=-=-= Room Layouts =-=-=-=-=
    #Load all standard room layout types
    for i in cls.roomLayoutDict:
      for n in range(cls.roomLayoutDict[i][0]): #Get how many layout variations to load
        scalepic = p.transform.scale(p.image.load("assets/newMaps/layout_"+i+str(n+1)+".png"),(roomSize,roomSize)) #scale image
        rawCollideList = "assets/newMaps/collisions/layout_"+i+str(n+1)+".txt" #Collisions file
        cls.roomLayoutDict[i][1].append(rawCollideList)
        cls.roomLayoutDict[i][2].append(scalepic)
    #Load special room layouts
    load = ['spawn','exit','chest']
    for i in load:
      scalepic = p.transform.scale(p.image.load("assets/newMaps/layout_"+i+".png"),(roomSize,roomSize)) #scale image
      rawCollideList = "assets/newMaps/collisions/layout_"+i+".txt" #Collisions file
      cls.specialRoomLayoutDict[i][1].append(rawCollideList)
      cls.specialRoomLayoutDict[i][2].append(scalepic)

  #Map generation methods
  def mrGenny(self): #mrGenny builds the map and checks that it meets the requirements
    while True:
      self.level = [[0 for i in range(self.mapSize)] for i in range(self.mapSize)] #Clear map
      #Plot a random even coordinate on map as the spawn point
      startX, startY = r.randint(1,(self.mapSize-1)//2-1)*2, r.randint(1,(self.mapSize-1)//2-1)*2
      self.level[startY][startX] = 5
      
      #Queue for rooms that have a chance of gaining another exit
      newRoomList = [(startX,startY)]

      exitSpawned = False
      
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
        newRoomChance = r.randint(0,int(10*self.complexity)) #VERY IMPORTANT IN STRUCTURE OF DUNGEON
        if newRoomChance < 10:
          del newRoomList[newRoomList.index((roomX,roomY))]
        
        for y in range(numOfExits): #Add new room
          direct = r.choice(directChoices) #choose direction
      
          if -1 < roomY+direct[1] < self.mapSize-1 and -1 < roomX+direct[0] < self.mapSize-1 and -1 < roomY+direct[1]*2 < self.mapSize-1 and -1 < roomX+direct[0]*2 < self.mapSize-1: #Check that the room is not next to a border
            if self.level[roomY+direct[1]][roomX+direct[0]] == 0 and self.level[roomY+direct[1]*2][roomX+direct[0]*2] == 0: #Check in a 2x1 rect in from of room that the space is avaliable
              self.level[roomY+direct[1]][roomX+direct[0]] = 2

              #Give a random chance for the room to be an exit room
              exitChance = r.randint(0,int(self.mapSize*1.5))
              chestChance = r.randint(0,int(self.mapSize*2))
              
              if exitChance == 0 and exitSpawned == False:
                self.level[roomY+direct[1]*2][roomX+direct[0]*2] = 6 #Convert room into an exit
              elif chestChance == 0:
                self.level[roomY+direct[1]*2][roomX+direct[0]*2] = 7 #Convert room into an exit
              else:
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
      chestCount = 0
      for i in range(len(self.level)):
        for n in range(len(self.level[i])):
          if self.level[i][n] == 1:
            roomCount += 1
          elif self.level[i][n] == 5:
            spawnCount += 1
          elif self.level[i][n] == 6:
            exitCount += 1
          elif self.level[i][n] == 7:
            chestCount += 1
      if 5 < roomCount < self.mapSize*2 and spawnCount == 1 and exitCount == 1 and chestCount > 0: #If the generated dungeon matches the requirements, stop generating
        break
      else:
        #print('regenerating')
        pass


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
        self.levelMap[i][n] = [self.level[i][n], directKey]

    
    #Match roomImage/hallwayImage with roomType/hallwayType
    for i in range(len(self.levelMap)): #For each map element in map
      for n in range(len(self.levelMap[i])):
        #If the map element is not empty
        if True:
        #if len(self.levelMap[i][n]) != 1:
          if self.levelMap[i][n][0] != 2 and self.levelMap[i][n][0] != 0: #If the map element is a room
            #Search roomDict for coresponding room type
            for q in MapGen.roomDict:
              for p in MapGen.roomDict[q]:
                if MapGen.roomDict[q][p][0] == self.levelMap[i][n][1]: #IF the roomtypes match, add the image to the list too
                  self.levelMap[i][n].append((q,p)) #room name
                  self.levelMap[i][n].append(MapGen.roomDict[q][p][-2]) #collision data location
                  self.levelMap[i][n].append(MapGen.roomDict[q][p][-1]) #room image
                  break
          elif self.levelMap[i][n][0] == 2: #If the map element is a hallway
            #Search hallwayDict for coresponding hallway type
            for q in MapGen.hallwayDict:
              for p in MapGen.hallwayDict[q]:
                if MapGen.hallwayDict[q][p][0] == self.levelMap[i][n][1]: #IF the hallwaytypes match, add the image to the list too
                  self.levelMap[i][n].append(MapGen.hallwayDict[q][p][-2])
                  self.levelMap[i][n].append(MapGen.hallwayDict[q][p][-1])
                  break
          elif self.levelMap[i][n][0] == 0: #Or if the map element is empty
              self.levelMap[i][n].append(MapGen.otherDict['none']['none'][-2])
              self.levelMap[i][n].append(MapGen.otherDict['none']['none'][-1])

          
  #MrRoomy assigns each room with a room layout (REQUIRES INIT TO BE CALLED)
  def mrRoomy(self):
    #Create clist of potetial layout types
    choiceList = [i for i in MapGen.roomLayoutDict]
      
    #assign a random layout type to each room
    for i in range(len(self.level)):
      for n in range(len(self.level[i])):

        if self.level[i][n] == 5: #IF the map element is a spawn room
          self.layoutMap[i][n] = [MapGen.specialRoomLayoutDict['spawn'][1][0],MapGen.specialRoomLayoutDict['spawn'][2][0]]
          
        elif self.level[i][n] == 6: #IF the map element is a exit room

          self.layoutMap[i][n] = [MapGen.specialRoomLayoutDict['exit'][1][0],MapGen.specialRoomLayoutDict['exit'][2][0]]

        elif self.level[i][n] == 7: #IF the map element is a chest room
          self.layoutMap[i][n] = [MapGen.specialRoomLayoutDict['chest'][1][0],MapGen.specialRoomLayoutDict['chest'][2][0]]
          
        elif self.level[i][n] == 1: #If the map element is a normal room
          #Generate a random room layout
          key = r.choice(choiceList) #pick and random layout type
          variation = r.randint(0,MapGen.roomLayoutDict[key][0]-1)
          #collisionMap = MapGen.importCollisionMap(MapGen.roomLayoutDict[key][1][variation]) #Import collision data from raw file
          self.layoutMap[i][n] = [MapGen.roomLayoutDict[key][1][variation],MapGen.roomLayoutDict[key][2][variation]] #Get image of room layout

          
  #mrCollidey loads the collision map of a room's walls and combines it with the room layout collision
  #Each room has two states and therefore two collision maps, open doors, and closed doors
  def mrCollidey(self): #mrCollidey also loads all the raw collision data from text files
    for i in range(len(self.level)): #For each map element
      for n in range(len(self.level[i])):
        if self.level[i][n] == 0 or self.level[i][n] == 2: #If there is no room here or a hallway, there is no need to merge layout with room
          self.roomCollide[i][n] = MapGen.importCollisionMap(self.levelMap[i][n][-2])
        elif self.level[i][n] != 0: #IF there is a room
          baseLayer = MapGen.importCollisionMap(self.levelMap[i][n][-2]) #Load the raw collision data of the room
          topLayer = MapGen.importCollisionMap(self.layoutMap[i][n][-2]) #Load the raw collision data of the room layout
          self.roomCollide[i][n] = MapGen.mergeCollideLayers(baseLayer,topLayer)


  #mrDoory places all the objects on map, like the doors and chests
  def mrObby(self,scale):
    exitTypes = ('R','U','L','D')
    #Determine what type of room each room is (to find out where the doors are)
    for i in range(len(self.levelMap)): #Iterate through map
      for n in range(len(self.levelMap[i])):
        if self.levelMap[i][n][0] != 2 and self.levelMap[i][n][0] != 0: #We only care if there are doors or not if it is a room
          #Determine the location of doors
          roomKey = () #Tuple indicating the exit postion of room

          if self.levelMap[i][n][2][0] == 'cap' or self.levelMap[i][n][2][0] == 'funnel' or self.levelMap[i][n][2][0] == 'L': #If the room is a normal room
            roomKey = tuple(self.levelMap[i][n][2][1])
          if self.levelMap[i][n][2][0] == 'hub': #if the room is a hub
            roomKey = ('R','U','L','D')
          elif self.levelMap[i][n][2][0] == 'T': #if the room is a T
            tempRoomKey = tuple(self.levelMap[i][n][2][1])
            
            roomKey = ()
            for q in exitTypes: #Rename T room
              if q not in tempRoomKey:
                roomKey += tuple(q)
                
          #Create rect objects for each door using list comp, first we determine the location of the door in the room, then we offset it by however many rooms it may be from the origin 
          self.doorPosList[i][n] = [[d,p.Rect(MapGen.doorDict[d][0]*scale+n*scale*self.mapSize,MapGen.doorDict[d][1]*scale+i*scale*self.mapSize, \
                                     MapGen.doorDict[d][2]*scale,MapGen.doorDict[d][3]*scale)] for d in roomKey]


        if self.levelMap[i][n][0] == 7: #If there is a chest room, place a chest in the center
          middleX, middleY = 7, 7 
          self.chestPosList.append([n,i,p.Rect(n*scale*self.mapSize+middleX*scale,i*scale*self.mapSize+middleY*scale,scale,scale)])

        #Create progress list (tells which rooms have been cleared)
        if self.level[i][n] == 1: #If the room is a normal room
          #Each room has 3 modes, unspawned (the player has not visited), unclear (there are still unkilled enemies), clear (all enemies are dead)
          self.progress[i][n] = 'unspawned'
        else:
          self.progress[i][n] = 'none'


#=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
MapGen.initGraphics(16)

myLevel = MapGen(16,3.2) #Create level map

myLevel.mrGenny() #Generate the room layout

pprint(myLevel.level)

myLevel.mrClassy() #Determine the type of room depending on the amount of exits has

myLevel.mrRoomy() #Generate the room layout of each room

myLevel.mrCollidey() #Merge the collsion data of the room and room layout

myLevel.mrObby(128)
#pprint(myLevel.doorPosList)
'''

