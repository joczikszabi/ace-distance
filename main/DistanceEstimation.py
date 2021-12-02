import os
import cv2
import json
import math
import numpy as np
import configparser
from scipy import spatial

class DistanceEstimation:
    def __init__(self, generateDummy = False):
        
        # Load config data from config file
        configParser = configparser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.txt')
        configParser.read(configFilePath)
        
        #self.focal_length = configParser.getfloat('CONFIG', 'CAMERA_FOCAL_LENGTH')
        #self.object_real_width = configParser.getfloat('CONFIG', 'OBJECT_REAL_WIDTH')

        self.distance_between_nodes = configParser.getfloat('CONFIG', 'DISTANCE_BETWEEN_NODES')

        if generateDummy:
            self.grid = self.generateDummyGrid()
        else:
            grid_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'grid.json')
            with open(grid_path, "r") as f:
                # IMPORTANT!!!!
                # SORT coordinates based on x and y coordinates and save them in a 2d array
                gridjson = json.load(f)
                self.grid = []
                for row in gridjson["nodes"]:
                    new_row = []

                    for node in row:
                        new_row.append(tuple(node))
                    self.grid.append(new_row)

                self.grid = np.array(self.grid)

    def generateDummyGrid(self):
        xvalues = np.linspace(0.0, 1920.0, num=20)
        yvalues = np.linspace(0.0, 1080.0, num=10)

        xx, yy = np.meshgrid(xvalues, yvalues)
        coords = [(a1, b1,) for a, b in zip(xx, yy) for a1, b1 in zip(a, b)]

        return coords


    def getClosestNode(self, coordinate):
    # Finds closest node in the grid to the coordinate(x, y)
    #
    # Input parameters:
    # coordinate(x, y): Touple where x and y coordinates are in pixels
    #
    # Returns:
    # Closest node to the given coordinate
        print(self.grid.flatten())
        return spatial.KDTree(self.grid.flatten()).query(coordinate)

    def findNextNodeVertical(self, node):
        minY = 10000
        nextNode = []

        for grid_point in self.grid:
            diffY = node[1] - grid_point[1]
            if abs(grid_point[0] - node[0 ]) < 60 and diffY > 0 and diffY < minY:
                nextNode = grid_point
                minY = diffY


        print(f"NextNode vertically: {nextNode}")
        return nextNode

    def findNextNodeHorizontal(self, node):
        minX = 10000
        nextNode = []

        for grid_point in self.grid:
            diffX = grid_point[0] - node[0]
            if abs(grid_point[1] - node[1]) < 40 and diffX > 0 and diffX < minX:
                nextNode = grid_point
                minX = diffX

        print(f"NextNode horizontally: {nextNode}")
        return nextNode


    def findNumberOfNodesBetween(self, node1, node2):
        numNodesX = 0
        nextNodeX = node1
        
        while True:
            nextNodeX = self.findNextNodeHorizontal(nextNodeX)

            if nextNodeX and nextNodeX[0] <= node2[0]:
                numNodesX += 1
            else:
                break

        numNodesY = 0
        nextNodeY = node1
        while True:
            nextNodeY = self.findNextNodeVertical(nextNodeY)

            if nextNodeY and node2[1] <= nextNodeY[1]:
                numNodesY += 1
            else:
                print("alma?")
                break

        print(f"xadj: {numNodesX} yadj: {numNodesY}")

        return [numNodesX, numNodesY]
    
    def estimateDistance(self, coordinate1, coordinate2):
        dist1, node_ind1 = self.getClosestNode(coordinate1)
        dist2, node_ind2 = self.getClosestNode(coordinate2)
        print(f"closest to ball: ({self.grid[node_ind1]})")
        print(f"closest to hole: ({self.grid[node_ind2]})")

        numNodesBetween = self.findNumberOfNodesBetween(self.grid[node_ind1], self.grid[node_ind2])

        a = numNodesBetween[0] * self.distance_between_nodes
        b = numNodesBetween[1] * self.distance_between_nodes

        dist = math.sqrt(a**2 + b**2)

        return dist