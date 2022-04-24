import json

import numpy as np

with open('../../layouts/layout2/grid.json', "r") as f:
    grid_json = json.load(f)
    grid = []

    for row in grid_json["nodes"]:
        new_row = []
        for node in row:
            if not node == []:
                x = node[0] + 440
                y = node[1] + 250
                node = (x, y)
            new_row.append(node)
        grid.append(new_row)

    grid = np.array(grid, dtype=object)

grid_json["nodes"] = grid.tolist()

with open(f"./tmp/grid_shifted.json", "w") as f:
    json.dump(grid_json, f)
