import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from helpers.load import loadConfig, loadLayout


class GridLayout:
    def __init__(self, layout_name=''):
        if layout_name == '':
            configParser = loadConfig()
            layout_name = configParser['GRID']['LAYOUT_NAME']

        self.grid_path = os.path.join(os.path.dirname(__file__), '..', 'layouts', f'{layout_name}', 'grid.json')
        self.layout = loadLayout(self.grid_path)

        self.cells = []
        self._setGridCells()

    def getContainingCell(self, point):
        for i in range(0, len(self.cells)):
            for j in range(0, len(self.cells[0])):
                if self.cells[i][j].isContained(point):
                    return self.cells[i][j]
        return False

    # Setters
    def _setGridCells(self):
        num_rows = self.layout['nodes'].shape[0]
        num_cols = self.layout['nodes'].shape[1]

        for i in range(0, num_rows - 1):
            row = []
            for j in range(0, num_cols - 1):
                cellid = i * self.layout['nodes'].shape[1] + j
                points = [self.layout['nodes'][i][j], self.layout['nodes'][i][j+1], self.layout['nodes'][i+1][j+1], self.layout['nodes'][i+1][j]]
                cell = GridCell(cellid=cellid, points=points, x=j, y=i)
                row.append(cell)

            self.cells.append(row)

    # Getters
    def getGridCells(self):
        return self.cells

    def getGridNodes(self):
        return self.layout['nodes']

    def getDistBetweenNodes(self):
        return self.layout['distance_between_nodes']

    def getDistBetweenCells(self, coordinate1, coordinate2):
        cell1 = self.getContainingCell(coordinate1)
        cell2 = self.getContainingCell(coordinate2)

        dist_x = abs(cell1.x - cell2.x) - 1
        dist_y = abs(cell1.y - cell2.y) - 1

        return dist_x, dist_y


class GridCell:
    def __init__(self, cellid, points, x, y):
        self.cellid = cellid
        self.points = points
        self.x = x
        self.y = y
        self.isClosed = all(map(len, points))
        self.polygon = Polygon(points) if self.isClosed else None

    def isContained(self, point):
        if not self.isClosed:
            return False
        return self.polygon.contains(Point(point))

    def getPoints(self):
        return self.points


