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

        self.distance_between_nodes = configParser.getfloat('CONFIG', 'DISTANCE_BETWEEN_NODES')
        self.grid_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'grid.json')

        if generateDummy:
            self.generateDummyGrid()
        else:
            self.loadGridFromJson()

            
    def loadGridFromJson(self):
        # Loads grid layout from json data file
        #
        # Returns: N x M numpy array containing the grid coordinates

        with open(self.grid_path, "r") as f:
            self.grid_json = json.load(f)
            grid = []

            for row in self.grid_json["nodes"]:
                new_row = []
                for node in row:
                    new_row.append(tuple(node))
                grid.append(new_row)

            self.grid = np.array(grid, dtype=object)


    def generateDummyGrid(self):
        xvalues = np.linspace(0.0, 1920.0, num=20)
        yvalues = np.linspace(0.0, 1080.0, num=10)

        xx, yy = np.meshgrid(xvalues, yvalues)
        coords = [(a1, b1) for a, b in zip(xx, yy) for a1, b1 in zip(a, b)]

        self.grid = coords


    def getClosestNode(self, coordinate):
        # Finds closest node in the grid to the coordinate(x, y)
        #
        # Input parameters:
        # coordinate(x, y): Touple where x and y coordinates are in pixels
        #
        # Returns:
        # Closest node to the given coordinate


        grid_flatten = [(node[0][0], node[0][1]) if node[0] != () else (9999, 9999) for node in self.grid.reshape(120,1)]
        print(grid_flatten)
        dist_ind = spatial.KDTree(grid_flatten).query(coordinate)

        # Convert back index to 2d array index format
        ind = (math.floor(dist_ind[1] / self.grid.shape[1]), dist_ind[1] % self.grid.shape[1])
        print((dist_ind[0], ind))
        return (dist_ind[0], ind)
    
    def estimateDistance(self, coordinate1, coordinate2):
        dist1, node_ind1 = self.getClosestNode(coordinate1)
        dist2, node_ind2 = self.getClosestNode(coordinate2)
        print(f"closest to ball: {self.grid[node_ind1[0], node_ind1[1]]}")
        print(f"closest to hole: {self.grid[node_ind2[0], node_ind2[1]]}")

        a = abs(node_ind1[0] - node_ind2[0]) * self.distance_between_nodes
        b = abs(node_ind1[1] - node_ind2[1]) * self.distance_between_nodes

        dist = math.sqrt(a**2 + b**2)

        return dist