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


        grid_flatten = [(node[0][0], node[0][1]) if node[0] != () else (9999, 9999) for node in self.grid.reshape(-1,1)]
        dist_ind = spatial.KDTree(grid_flatten).query(coordinate)

        # Convert back index to 2d array index format
        print(f"shape: {dist_ind}")
        ind = (math.floor(dist_ind[1] / self.grid.shape[1]), dist_ind[1] % self.grid.shape[1])
        return (dist_ind[0], ind)


    def calcResidual(self, coordinate, closest_node_idx):
        # Calculates residual in terms of meters

        # Convert to numpy array
        coordinate = np.asarray(coordinate)

        # Project vector on line defiend by x_prev and x
        tmp = np.asarray(self.grid[closest_node_idx[0], closest_node_idx[1]])
        if tmp[0] < coordinate[0]:
            x = np.asarray(self.grid[closest_node_idx[0], closest_node_idx[1]+1])
            x_prev = tmp

            l2 = np.sum((x_prev-x)**2)
            t = np.sum((coordinate - x_prev) * (x - x_prev)) / l2
            percentage_x = 1 - t
            projection_x = x_prev + t * (x - x_prev)

        else:
            x = tmp
            x_prev = np.asarray(self.grid[closest_node_idx[0], closest_node_idx[1]-1])

            l2 = np.sum((x_prev-x)**2)
            t = np.sum((coordinate - x_prev) * (x - x_prev)) / l2
            percentage_x = t
            projection_x = x_prev + t * (x - x_prev)
            
        print(f"indexes {closest_node_idx[0]} {closest_node_idx[1]}")
        print(f"x={x}")
        print(f"x_prev={x_prev}")
        print(f"l2={l2}")
        print(f"coordinate:{coordinate}")
        print(f"t={t}")
        print(f"projection x={projection_x}")

        # Project vector on line defiend by y_prev and y
        tmp = np.asarray(self.grid[closest_node_idx[0], closest_node_idx[1]])
        if tmp[1] < coordinate[1]:
            y = np.asarray(self.grid[closest_node_idx[0] + 1, closest_node_idx[1]])
            y_prev = tmp

            l2 = np.sum((y_prev-y)**2)
            t = np.sum((coordinate - y_prev) * (y - y_prev)) / l2
            percentage_y = 1 - t
            projection_y = y_prev + t * (y - y_prev)

        else:
            y = tmp
            y_prev = np.asarray(self.grid[closest_node_idx[0] - 1, closest_node_idx[1]])

            l2 = np.sum((y_prev-y)**2)
            t = np.sum((coordinate - x_prev) * (y - y_prev)) / l2
            percentage_y = t
            projection_y = y_prev + t * (y - y_prev)

        #print(f"percentage y={percentage_y}")
        print(f"projection={(percentage_x, percentage_y)}")
        return [[percentage_x, percentage_y], [projection_x, projection_y]]
        #return (percentage_x, percentage_y)
    
    def estimateDistance(self, coordinate1, coordinate2):
        dist1, node_ind1 = self.getClosestNode(coordinate1)
        dist2, node_ind2 = self.getClosestNode(coordinate2)
        print(f"closest to ball: {self.grid[node_ind1[0], node_ind1[1]]} {node_ind1}")
        print(f"closest to hole: {self.grid[node_ind2[0], node_ind2[1]]} {node_ind2}")

        resp1 = self.calcResidual(coordinate1, node_ind1)
        resp2 = self.calcResidual(coordinate2, node_ind2)

        a = abs(node_ind1[0] - node_ind2[0]) * self.distance_between_nodes + 0
        b = abs(node_ind1[1] - node_ind2[1]) * self.distance_between_nodes + 0

        dist = math.sqrt(a**2 + b**2)

        return [dist, resp1[1]]
        #return (dist, [percentages1, percentages2])