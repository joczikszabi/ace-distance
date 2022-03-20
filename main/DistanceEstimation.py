import os
import cv2
import json
import math
import numpy as np
import configparser
from scipy import spatial


class DistanceEstimation:
    def __init__(self, generate_dummy=False, grid_layout=''):

        if grid_layout == '':
            # Load config data from config file
            configParser = configparser.ConfigParser()
            configFilePath = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.txt')
            configParser.read(configFilePath)
            grid_layout = configParser['GRID']['LAYOUT_NAME']

        self.grid_path = os.path.join(os.path.dirname(__file__), '..', 'layouts', f'{grid_layout}', 'grid.json')

        if generate_dummy:
            self.generateDummyGrid()
        else:
            self.loadGridFromJson()

    def loadGridFromJson(self):
        # Loads grid layout from json data file and its corresponding data
        # such as the distance between adjacent grid nodes (in meters)

        with open(self.grid_path, "r") as f:
            self.grid_json = json.load(f)
            grid = []

            for row in self.grid_json["nodes"]:
                new_row = []
                for node in row:
                    new_row.append(tuple(node))
                grid.append(new_row)

            self.grid = np.array(grid, dtype=object)
            self.distance_between_nodes = self.grid_json["distance_between_nodes"]

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

        grid_flatten = [(node[0][0], node[0][1]) if node[0] != () else (9999, 9999) for node in
                        self.grid.reshape(-1, 1)]
        dist_ind = spatial.KDTree(grid_flatten).query(coordinate)

        # Convert back index to 2d array index format
        ind = (math.floor(dist_ind[1] / self.grid.shape[1]), dist_ind[1] % self.grid.shape[1])
        return dist_ind[0], ind

    def getAdjNodes(self, coordinate):
        dist, closest_node_ind = self.getClosestNode(coordinate)
        closest_node = np.asarray(self.grid[closest_node_ind[0], closest_node_ind[1]])

        try:
            # Get adjacent nodes on x axis
            if closest_node[0] < coordinate[0]:
                prev_node_x = closest_node
                next_node_x = np.asarray(self.grid[closest_node_ind[0], closest_node_ind[1] + 1])

            else:
                prev_node_x = np.asarray(self.grid[closest_node_ind[0], closest_node_ind[1] - 1])
                next_node_x = closest_node

            # Get adjacent nodes on y axis
            if closest_node[1] < coordinate[1]:
                prev_node_y = closest_node
                next_node_y = np.asarray(self.grid[closest_node_ind[0] + 1, closest_node_ind[1]])

            else:
                prev_node_y = np.asarray(self.grid[closest_node_ind[0] - 1, closest_node_ind[1]])
                next_node_y = closest_node
        except:
            print('Position out of grid layout!')
            return None

        adj_nodes = {
            "x": {
                "prev": prev_node_x,
                "next": next_node_x
            },
            "y": {
                "prev": prev_node_y,
                "next": next_node_y
            },
            "closest": closest_node
        }
        return adj_nodes

    def projectCoordinate(self, coordinate, axis="x"):
        # Projects the given coordinates on perpendicular basis vectors
        # Ref: https://stackoverflow.com/questions/61341712/calculate-projected-point-location-x-y-on-given-line-startx-y-endx-y

        adj_nodes = self.getAdjNodes(coordinate)
        # cv2.circle(self.img, (adj_nodes['closest'][0], adj_nodes['closest'][1]), 2, (100, 200, 0), -1)

        p0 = adj_nodes[axis]["prev"]
        p1 = adj_nodes[axis]["next"]

        l2 = np.sum((p0 - p1) ** 2)
        t = np.sum((coordinate - p0) * (p1 - p0)) / l2

        projection = p0 + t * (p1 - p0)
        return t, projection

    def calcResidual(self, coordinate1, coordinate2):
        # Calculates residuals in terms of meters

        # Project coordinates
        t_x, projection_x = self.projectCoordinate(coordinate1, "x")
        t_y, projection_y = self.projectCoordinate(coordinate1, "y")

        factor_x = (1 - t_x) if (t_x > 0.5) else t_x
        factor_y = (1 - t_y) if (t_y > 0.5) else t_y

        adj_nodes_1 = self.getAdjNodes(coordinate1)
        adj_nodes_2 = self.getAdjNodes(coordinate2)

        min_x = min(adj_nodes_1["closest"][0], adj_nodes_2["closest"][0])
        max_x = max(adj_nodes_1["closest"][0], adj_nodes_2["closest"][0])
        if min_x <= projection_x[0] <= max_x:
            residual_coefficient_x = -1
        else:
            residual_coefficient_x = 1

        min_y = min(adj_nodes_1["closest"][1], adj_nodes_2["closest"][1])
        max_y = max(adj_nodes_1["closest"][1], adj_nodes_2["closest"][1])
        if min_y <= projection_y[1] <= max_y:
            residual_coefficient_y = -1
        else:
            residual_coefficient_y = 1

        residual_x = self.distance_between_nodes * factor_x * residual_coefficient_x
        residual_y = self.distance_between_nodes * factor_y * residual_coefficient_y

        return residual_x, residual_y

    def estimateDistance(self, coordinate1, coordinate2, img):
        self.img = img

        if coordinate1 is None or coordinate2 is None:
            return None

        adj_nodes1 = self.getAdjNodes(coordinate1)
        adj_nodes2 = self.getAdjNodes(coordinate2)

        if adj_nodes1 is None or adj_nodes2 is None:
            return None

        dist1, node_ind1 = self.getClosestNode(coordinate1)
        dist2, node_ind2 = self.getClosestNode(coordinate2)

        residual1 = self.calcResidual(coordinate1, coordinate2)
        residual2 = self.calcResidual(coordinate2, coordinate1)

        a = abs(node_ind1[0] - node_ind2[0]) * self.distance_between_nodes + (residual1[0] + residual2[0])
        b = abs(node_ind1[1] - node_ind2[1]) * self.distance_between_nodes + (residual1[1] + residual2[1])

        dist = round(math.sqrt(a ** 2 + b ** 2), 2)

        return dist
