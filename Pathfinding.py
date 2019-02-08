#Daniel Liu - ryyaan
from pprint import *


#Extract map collision data from file
def importCollisionMap(rawMapData,tileSize,mapSize):
    #Read from file to extrace collisions
    rawData = open(rawMapData).readlines()
    #Create a 2d array to get the position of the map rect
    rawCollideList = [i.replace('\n','').split(' ') for i in rawData] #clean up file 

    return rawCollideList
        

#Class for enemy ai
class Pathfinding:

    #Utility Functions (These assist the main ai algorithms
    @staticmethod
    #Function that creates grid with collision objects along with a tuple that indicates location 
    def graph(grid):
      for i in range(len(grid)): #Iterate through graph
        for n in range(len(grid[i])):
            collide = None
            if int(grid[i][n]) == 1 or int(grid[i][n]) == 2: #if the collide block is a solid rect, mark it down as a solid rect
                collide = 1
            else:
                collide = 0
            grid[i][n] = (collide,(n,i))
          
      return grid
    
    @staticmethod
    #Converts collision grid from rect objects to 1s and 0s
    def simplify(grid):
        simple = [[None for n in range(len(grid))] for i in range(len(grid))]
        for i in range(len(grid)):
            for n in range(len(grid[i])):
                if grid[i][n] == []:
                    simple[i][n] = 0
                else:
                    simple[i][n] = 1

        return simple
                   
    @staticmethod
    #Function that returns the top priority node
    def pop(queue):
      optimal = (10**6,10**6) #Tuple that indicates the node's (index,cost), the default is infinity
      for i in range(len(queue)):
        if queue[i][0] < optimal[1]: #If the cost of this node is the least, make this the highest priority node (the first element in each tuple is it's priority)
          optimal = (i,queue[i][0])
          
      #return the index of the highest priority node
      return optimal[0]
    

    #AI Functions
    
    @staticmethod
    #Finds the shortest path from point A to point B
    def traceAI(startX,startY,endX,endY,grid): #startpos is the map element location of the entity on the grid
        
        queue = [(0,startX,startY)] #queue of nodes to explore
        paths = {} #Dict of all paths to destination
        costs = {(startX,startY):0} #Dict of all the cost to get to each node
        direct = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
        
        while len(queue) != 0:  #While the queue is not empty
          
          #Update current node as the first item in the queue and then pop it
          index = Pathfinding.pop(queue) #Find the highest priority node in the queue
          curX, curY = queue[index][1], queue[index][2]

          #If the end point has the highest priority in the queue, terminate the algorithm
          if queue[index][1] == endX and queue[index][2] == endY:
            break

          #Pop the highest priority node
          queue.pop(index)
         
          #Apporixmate the distance to destination usng manhattan distance
          heuristic = abs(curX-endX) + abs(curY-endY)
          
          for d in range(len(direct)): #For each adjacent node
            adjX, adjY = curX+direct[d][0], curY+direct[d][1]

            #Dont allow ai to cross corners
            nodeindex = direct.index((direct[d][0],direct[d][1]))

            #If the new node is a diagonal move, check it's left and right nodes
            ln, rn = nodeindex, nodeindex #default to current node
            if nodeindex%2 == 1:
                ln, rn = nodeindex-1, nodeindex+1
                
                if nodeindex == len(direct)-1: #if the node is the last one, check the beginning of the list
                    rn = 0

            lgx, lgy, rgx, rgy = curX+direct[ln][0], curY+direct[ln][1], curX+direct[rn][0], curY+direct[rn][1]
                
            
            #Make sure to not backtrack or go off map or go into a collision object or cross corners
            if (adjX,adjY) not in costs and 0 <= adjX < len(grid) and 0 <= adjY < len(grid) and grid[adjY][adjX][0] == 0 and (grid[lgy][lgx][0] == 0 and grid[rgy][rgx][0] == 0):
              costToMove = ((adjX-curX)**2+(adjY-curY)**2)**0.5 #Distance formula from node to adjacent node
              newCost = costs[(curX,curY)] + costToMove #Total cost to move to node from start point
              
              if newCost not in costs or newCost < costs[(adjX,adjY)]: #Add new cost to node if it is not in the list or if this path is a more efficient way of getting to that node
                costs[(adjX,adjY)] = newCost #update/add cost
                
                #Apporixmate the distance to destination usng manhattan distance
                heuristic = abs(adjX-endX) + abs(adjY-endY)
                
                priority = heuristic + newCost #prioritize the node depending on it's cost to get there and it's distance to the destination
                paths[(adjX,adjY)] = curX,curY #Update the node we came from to reach the adjacent node
                queue.append((priority,adjX,adjY)) #Add the new node to the priority queue
            
          #Make ai stand still if the end point is unreachable
          if len(queue) == 0:
              pathList = [(startX,startY)]
              return pathList #exit function early
            
        #Trace the path from the end point to the start point
        pathX, pathY = endX, endY
        pathList = [(endX,endY)]
        while True:
          if pathX == startX and pathY == startY: #Stop when you reach the start point
            break
        
          node = paths[(pathX,pathY)]
          pathList.append(node) #Add node to path
          pathX, pathY = node[0], node[1]
          

        #pathList.reverse() #invert list so the path starts at the start point
        
        #print(pathList)
        return pathList

    '''
    @staticmethod
    #This ai heads in a random direction, and changes direction when it hits something
    def roamAI(startX,startY,pathLength,grid):
        direct = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)] #The potential directions the ai can choose to go in
        curX, curY = startX, startY
        for i in range(pathLength): #The path the ai finds is finite, as the function needs to end
            #Create a queue of the directions to travel in 
            directList = [r.choice(direct)] #Choose a general direction to go
            [d for d in direct if d != travelDirect].extend(directList)
            for n in range(directList):
                adjX, adjY = curX+directList[n][0], curY+directList[n][1]
                if int(grid[adjX][adjY]) == 1: #If there is a collision object
                    
    '''
            

'''
grid = importCollisionMap('assets/maps/collisions/room_coll_pftest.txt',128,16)
grid = Pathfinding.graph(grid)
pathList = Pathfinding.traceAI(7,6,14,15,grid)

#Graphics test
import pygame as p

#Scale Variables
scale = 32
playerScale = 50

#Init calls
p.init()

#Set up screen
screenX, screenY = 800,600
screen = p.display.set_mode((screenX, screenY))
centerX, centerY = int(screenX/2), int(screenY/2)


#draw collisions
for i in range(len(grid)):
    for n in range(len(grid[i])):
        if grid[i][n][0] == 1:
            p.draw.rect(screen,(255,0,0),(n*scale,i*scale,scale,scale))
        if grid[i][n][0] == 0:
            p.draw.rect(screen,(255,255,255),(n*scale,i*scale,scale,scale))


#pathfinding
for i in range(len(pathList)):
    p.draw.rect(screen,(0,255,255),(pathList[i][0]*scale,pathList[i][1]*scale,scale,scale))
    
    p.display.flip()
    p.time.delay(100)

p.display.flip()
p.time.delay(4000)
p.quit()      
'''
