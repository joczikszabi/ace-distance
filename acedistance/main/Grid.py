import os
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from acedistance.helpers.load import loadLayout


class GridLayout:
    def __init__(self, layout_name):
        self.grid_path = os.path.join(os.path.dirname(__file__), '..', 'layouts', f'{layout_name}', 'grid.json')
        if not os.path.isfile(self.grid_path):
            raise FileNotFoundError(f'Layout definition file not found: {self.grid_path}')

        self.layout = loadLayout(self.grid_path)

        self.cells = []
        self._setGridCells()

    def getContainingCell(self, p):
        """
        Getter function returning the GridCell which covers the given point.

        Args:
            p (np.array): Coordinate of point

        Returns:
            GridCell: GridCell which covers the given point.
        """
        for i in range(0, len(self.cells)):
            for j in range(0, len(self.cells[0])):
                if self.cells[i][j].isContained(p):
                    return self.cells[i][j]
        return False

    # Setters
    def _setGridCells(self):
        """
        Sets up the grid cells using the node positions in the layout settings file

        Args:

        Returns:
        """
        num_rows = self.layout['nodes'].shape[0]
        num_cols = self.layout['nodes'].shape[1]

        for i in range(0, num_rows - 1):
            row = []
            for j in range(0, num_cols - 1):
                cellid = i * self.layout['nodes'].shape[1] + j
                points = [self.layout['nodes'][i][j], self.layout['nodes'][i][j+1], self.layout['nodes'][i+1][j+1], self.layout['nodes'][i+1][j]]
                cell = GridCell(cellid=cellid, points=points, x=i, y=j)
                row.append(cell)

            self.cells.append(row)

    # Getters
    def getGridCells(self):
        """
        Getter function returning all of the grid cells used in the layout.

        Args:

        Returns:
            [GridCell]: Returns the GridCells in this grid layout.
        """

        return self.cells

    def getGridNodes(self):
        """
        Getter function returning the nodes in the grid layout.

        Args:

        Returns:
            list: List of the nodes in this grid layout.
        """

        return self.layout['nodes']

    def getDistBetweenNodes(self):
        """
        Getter function returning the distance between two adjacent nodes in the grid layout.

        Args:

        Returns:
            Float: Distance between nodes in terms of meter
        """

        return self.layout['distance_between_nodes']

    def distCoordinates(self, p1, p2):
        """
        Returns the number of grid cells between two coordinates (in both axes).

        Args:
            p1 (tuple(int, int)): First coordinate
            p2 (tuple(int, int)): Second coordinate

        Returns:
            tuple(int, int): Difference between the two coordinates in terms of
                grid cells both horizontally and vertically respectively.
        """


        cell1 = self.getContainingCell(p1)
        cell2 = self.getContainingCell(p2)

        dist_x = max(0, abs(cell1.y - cell2.y) - 1)
        dist_y = max(0, abs(cell1.x - cell2.x) - 1)

        return dist_x, dist_y


class GridCell:
    def __init__(self, cellid, points, x, y):
        self.cellid = cellid
        self.points = np.array(points, dtype=object)
        self.x = x
        self.y = y
        self.isClosed = all(map(len, points))
        self.polygon = Polygon(points) if self.isClosed else None

    def isContained(self, p):
        """
        Checks if the given point is inside this cell or no.

        Args:
            p (np.array): Coordinate of point

        Returns:
            GridCell: GridCell which covers the given point.
        """

        if not self.isClosed:
            return False
        return self.polygon.covers(Point(p))

    def getPoints(self):
        """
        Getter function returning the points in this cell.

        Args:

        Returns:
            GridCell: Points in this cell.
        """

        return self.points

    def row(self):
        """Returns the row number in which the cell is contained in the GridLayout

        Args:

        Returns:
            int: Row number in the GridLayout where the cell is at.
        """
        return self.x

    def col(self):
        """Returns the column number in which the cell is contained in the GridLayout

        Args:

        Returns:
            int: Column number in the GridLayout where the cell is at
        """
        return self.y


