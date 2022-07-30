import os
import json
import numpy as np
import configparser


def loadConfig():
    """ Loads config data from config file

    Args:

    Returns:
        configparser: Config data in config.ini
    """

    parser = configparser.ConfigParser()
    configFilePath = os.path.join(os.path.dirname(__file__), '', '..', 'config', 'config.ini')
    parser.read(configFilePath)

    return parser


def loadLayout(layout_name):
    """ Loads grid layout from json data file and its corresponding data such as the distance between
    adjacent grid nodes (in meters)

    Args:
        layout_name (str): Layout name (stored in acedistance/layouts)

    Returns:
        object: Layout data in grid.json
    """

    layout_path = os.path.join(os.path.dirname(__file__), '..', 'layouts', f'{layout_name}', 'grid.json')
    if not os.path.isfile(layout_path):
        raise FileNotFoundError(f'Layout definition file not found: {layout_path}')

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
