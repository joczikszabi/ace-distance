import json

import numpy as np

with open('grid.json', "r") as f:
    grid_json = json.load(f)
    grid = []

    for row in grid_json["nodes"]:
        new_row = []
        for node in row:
            new_row.append(node)
        grid.append(new_row)

    grid = np.array(grid, dtype=object)

grid = np.transpose(grid)
print(grid.shape)

grid_points = {
    "nodes": grid.tolist()
}

print(grid)

with open(f"./grid_transposed.json", "w") as f:
    json.dump(grid_points, f)