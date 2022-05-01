import json
import numpy as np

with open('grid.json', "r") as f:
    grid_json = json.load(f)
    grid = np.array(grid_json["nodes"], dtype=object)

shp = grid.shape
out = [[None for _ in range(shp[0])] for _ in range(shp[1])]

for i in range(0, shp[1]):
    for j in range(0, shp[0]):
        out[i][j] = grid[j, i]


grid_points = {
    "nodes": out
}

with open(f"./grid_transposed_custom.json", "w") as f:
    json.dump(out, f)
