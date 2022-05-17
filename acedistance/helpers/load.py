import os
import json
import numpy as np
import configparser


# Load config data from config file
def loadConfig():
    parser = configparser.ConfigParser()
    configFilePath = os.path.join(os.path.dirname(__file__), '', '..', 'config', 'config.ini')
    parser.read(configFilePath)

    return parser


# Loads grid layout from json data file and its corresponding data
# such as the distance between adjacent grid nodes (in meters)
def loadLayout(layout_path):

    with open(layout_path, 'r') as f:
        grid_json = json.load(f)
        grid = []

        for row in grid_json['nodes']:
            new_row = []
            for node in row:
                new_row.append(tuple(node))
            grid.append(new_row)

        grid_json['nodes'] = np.array(grid, dtype=object)
        return grid_json
