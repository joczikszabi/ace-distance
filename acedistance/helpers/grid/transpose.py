import json

import numpy as np

with open('grid.json', "r") as f:
    grid_json = json.load(f)
    grid = np.array(grid_json["nodes"], dtype=object)

grid_t = np.transpose(grid)
print(grid_t.shape)

grid_points = {
    "nodes": grid_t.tolist()
}

with open(f"./grid_transposed.json", "w") as f:
    json.dump(grid_points, f)