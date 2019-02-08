import pygame as p
import math as m
from pprint import *

#Collision class for map
class Collider:

    @staticmethod
    #convert raw map collision data into rects (USED ONLY FOR MAPS
    def importCollisionMap(chunkX,chunkY,mapSize,rawMapData,tileSize):
        #convert tileRect 2d list to a normal list
        rawMapCollide = []
        for i in range(len(rawMapData)): #Iterate through 2d array
            for n in range(len(rawMapData[i])):
                if int(rawMapData[i][n]) != 0: #Add rect value to list if there is a collision list
                    rawMapCollide.append([rawMapData[i][n],p.Rect(n*tileSize+chunkX*mapSize*tileSize,i*tileSize+chunkY*mapSize*tileSize,tileSize,tileSize)])

        return rawMapCollide

    
    @staticmethod
    #convert collision data into a 2d array (USED FOR MAPS ONLY)
    def convertCollisionGrid(chunkX,chunkY,rawCollisionData,tileSize,mapSize):
        collideList = [[[] for i in range(mapSize)] for n in range(mapSize)]
        #Create a 2d array of collision objects from the 1d lists by rounding their positions to the nearest map element
        for i in range(len(rawCollisionData)):
            #Add collision to 2d array if there is a collision (if there is no collision, there is no need to append None as each map element is represented as a list)
            rectX, rectY = rawCollisionData[i][-1][0]-chunkX*mapSize*tileSize, rawCollisionData[i][-1][1]-chunkY*mapSize*tileSize  #The position of the collision rects
            roundX, roundY = int(rectX/tileSize), int(rectY/tileSize) #Round the collision rect positions to the nearest map elements
            #Append the collision data into 2d list of lists (the map elements are lists as collision objects may round to same map element
            collideList[roundY][roundX] = rawCollisionData[i]

        return collideList
    

    @staticmethod
    #convert collision data into a 2d array (GENERAL USE)
    def convertCollisionGrid2(chunkX,chunkY,rawCollisionData,tileSize,mapSize):
        collideList = [[[] for i in range(mapSize)] for n in range(mapSize)]
        #Create a 2d array of collision objects from the 1d lists by rounding their positions to the nearest map element
        for i in range(len(rawCollisionData)):
            #Add collision to 2d array if there is a collision (if there is no collision, there is no need to append None as each map element is represented as a list)
            if rawCollisionData[i] != []:
                rectX, rectY = rawCollisionData[i][0]-chunkX*mapSize*tileSize, rawCollisionData[i][1]-chunkY*mapSize*tileSize  #The position of the collision rects
                roundX, roundY = int(rectX/tileSize), int(rectY/tileSize) #Round the collision rect positions to the nearest map elements
                #Append the collision data into 2d list of lists (the map elements are lists as collision objects may round to same map element
                collideList[roundY][roundX].append(rawCollisionData[i])

        return collideList

    
    @staticmethod
    #Find the collisions that are close to the entity (MAPS ONLY)
    def localCollision(chunkX,chunkY,entityRect,collLayer,tileSize,mapSize): 
        direct = [(-1,-1),(0,-1),(1,-1),(2,-1),(-1,0),(0,0),(1,0),(2,0),(-1,1),(0,1),(1,1),(2,1),(-1,2),(0,2),(1,2),(2,2)] #direction of adjacent cells to check for collisions
            
        #Return a list of rects that the main entity cannot collide with
        collideList = []
        
        #Round the position of the entity rect to the nearest element
        entityX, entityY = int(entityRect[0]/tileSize), int(entityRect[1]/tileSize)

        #For each direction to check for collide objects
        for i in range(len(direct)):
            if 0 <= entityX+direct[i][0]-chunkX*mapSize < 16 and 0 <= entityY+direct[i][1]-chunkY*mapSize < 16: #Make sure that the collision scan doesnt go off the list
                if collLayer[entityY+direct[i][1]-chunkY*mapSize][entityX+direct[i][0]-chunkX*mapSize] != []:
                    #Make sure that the tag of the collision object tells us that the object is collidable
                    if collLayer[entityY+direct[i][1]-chunkY*mapSize][entityX+direct[i][0]-chunkX*mapSize][0] == '1' or collLayer[entityY+direct[i][1]-chunkY*mapSize][entityX+direct[i][0]-chunkX*mapSize][0] == '2':
                        adjacentCell = collLayer[entityY+direct[i][1]-chunkY*mapSize][entityX+direct[i][0]-chunkX*mapSize]
                        collideList.append(adjacentCell)
                    
        return collideList


    @staticmethod
    #Find the collisions that are close to the entity (GENERAL USE)
    def localCollision2(chunkX,chunkY,entityRect,collLayer,tileSize,mapSize): 
        direct = [(-1,-1),(0,-1),(1,-1),(2,-1),(-1,0),(0,0),(1,0),(2,0),(-1,1),(0,1),(1,1),(2,1),(-1,2),(0,2),(1,2),(2,2)] #direction of adjacent cells to check for collisions
            
        #Return a list of rects that the main entity cannot collide with
        collideList = []
        
        #Round the position of the entity rect to the nearest element
        entityX, entityY = int(entityRect[0]/tileSize), int(entityRect[1]/tileSize)

        #For each direction to check for collide objects
        for i in range(len(direct)):
            if 0 <= entityX+direct[i][0]-chunkX*mapSize < 16 and 0 <= entityY+direct[i][1]-chunkY*mapSize < 16: #Make sure that the collision scan doesnt go off the list
                for n in range(len(collLayer[entityY+direct[i][1]-chunkY*mapSize][entityX+direct[i][0]-chunkX*mapSize])): #For each colide object in the adjacent cell
                    adjacentCell = collLayer[entityY+direct[i][1]-chunkY*mapSize][entityX+direct[i][0]-chunkX*mapSize][n]
                    collideList.append(adjacentCell)
                    
        return collideList
    
    @staticmethod
    #finds the bounding rect that bounds all the non opaque bits in an image
    def getBoundingRect(image):
        mask = p.mask.from_surface(image) #get mask of image
        boundingMask = mask.get_bounding_rects()
        
        return boundingMask[0] #return rect as just a rect object, not list


'''
#Scale Variables
scale = 128
playerScale = 200

#Import test images
#Players
playerPic = p.transform.scale(p.image.load('assets/players/martialArtist_player.png'), (playerScale,playerScale))
#Maps
demoMap = p.transform.scale(p.image.load('assets/maps/room_hub_hub.png'), (scale,scale))

#Create objects 
#Create collide objects

rawMapCollide = Collider.importCollisionMap('assets/maps/collisions/room_coll.txt',128,16)
mapCollide = Collider.convertCollisionGrid(rawMapCollide,128,16)

rawPlayerCollide = [p.Rect(129,56,100,100)]
playerCollide = Collider.convertCollisionGrid(rawPlayerCollide,128,16)
'''
