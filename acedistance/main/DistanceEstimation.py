import math
import numpy as np
from shapely.geometry import Point, LineString


class DistanceEstimation:
    def __init__(self, gridlayout):
        self.gridlayout = gridlayout
        self.directions = []

    def getAdjNodes(self, coordinate):
        """
        Gives back the position of nodes adjacent to the given coordinate

        Args:
            coordinate (tuple(Int, Int)): Coordinate of object

        Returns:
            Dictionary: Adjacent nodes to the given coordinate (top-left, top-right, bottom-left, bottom-right
        """

        cell = self.gridlayout.getContainingCell(coordinate)

        if not cell:
            raise ValueError('Position out of grid!')

        points = cell.getPoints()
        return {
            'tl': points[0],
            'tr': points[1],
            'br': points[2],
            'bl': points[3]
        }

    def calcResidualByProjection(self, p, a, b):
        """
        Projects the given coordinate on the line defined by a and b and calculates the distance between that point and a.
        Ref: https://stackoverflow.com/questions/61341712/calculate-projected-point-location-x-y-on-given-line-startx-y-endx-y

        Args:
            p (tuple(Int, Int)): Coordinate of point
            a (tuple(int, int)): First point on line
            b (tuple(int, int)): Second point on line

        Returns:
            Float: The distance between the given coordinate p and a in terms of meter
        """

        ap = p - a
        ab = b - a
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0, min(1, t))  # will map point p on the line segment
        pp = a + t * ab  # projected point
        residual = self.gridlayout.getDistBetweenNodes() * t

        return residual

    def calcResidualByIntersection(self, p, a, b):
        """
        A weaker version of calcResidualByProjection() where instead of projecting the given coordinate p on the line
        defined by the points a and b, we calculate the intersection of a horizontal line going through p
        and the line defined by a and b to find the "projected" point.

        Args:
            p (tuple(Int, Int)): Coordinate of point
            a (tuple(int, int)): First point on line
            b (tuple(int, int)): Second point on line

        Returns:
            Float: The distance between the given coordinate p and a in terms of meter
        """

        grid_vertical_sideline = LineString([a, b])
        max_x = max([v[0] for v in self.getAdjNodes(p).values()])
        horizontal_line = LineString([(0, p[1]), (max_x, p[1])])

        intersected_point = grid_vertical_sideline.intersection(horizontal_line)
        intersected_point = np.array([intersected_point.x, intersected_point.y])
        residual = self.calcResidualByProjection(intersected_point, a, b)

        return residual

    def getClosestSide(self, p0, p1, p2, p3, coordinate):
        """
        Given two lines (each defined by two points), the function returns the closest side to the given coordinate

        Args:
            p0 (tuple(int, int)): First point on line1
            p1 (tuple(int, int)): Second point on line1
            p2 (tuple(int, int)): First point on line2
            p3 (tuple(int, int)): Second point on line2
            coordinate (tuple(Int, Int)): Coordinate of object

        Returns:
            Int, Int: Returns the line (defined by two points) which is closest to the given coordinate
        """

        p = Point(coordinate)
        l1 = LineString([p0, p1])
        l2 = LineString([p2, p3])

        d1 = l1.distance(p)
        d2 = l2.distance(p)

        if d1 < d2:
            return p0, p1

        return p2, p3

    def calcResidualXBall(self, coordinate):
        """
        Calculates the horizontal distance between the coordinate of the ball and its enclosing grid cell.
        Since we can be certain that the ball is positioned left relative to the hole, we only need to focus on the
        distance between the coordinate of the ball and the right side of its enclosing grid cell.

        First it needs to find the line (defined by two points) onto which the ball is projected.
        There are two options to choose from:
            - 1. Top horizontal line defined by the grid points: top right and top left
            - 2. Bottom horizontal line defined by the grid points: bottom right and bottom left
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.

        Args:
            coordinate (tuple(Int, Int)): Coordinate of the ball which should be projected onto one of the
            horizontal sides of its enclosing grid cell.

        Returns:
            Bool: Returns the distance of how far the coordinate of the ball is from the right side of its grid cell.
        """

        adj_nodes = self.getAdjNodes(coordinate)
        p0, p1 = self.getClosestSide(adj_nodes['tr'],
                                     adj_nodes['tl'],
                                     adj_nodes['br'],
                                     adj_nodes['bl'],
                                     coordinate)

        residual = self.calcResidualByProjection(coordinate, p0, p1)

        self.directions.append('Ball X: RIGHT')

        return residual

    def calcResidualYBall(self, coordinate, coordinate_hole):
        """
        Calculates the vertical distance between the coordinate of the ball and the top (or bottom) side of its enclosing grid cell.

        First it needs to find the line (defined by two points) onto which the ball is projected.
        There are two options to choose from:
            - 1. Right vertical line defined by the grid points: top left and bottom left
            - 2. Left vertical line defined by the grid points: top right and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.

        Depending on where the hole is vertically located relative to the ball (top or bottom), the algorithm will
        return the vertical distance between the coordinate of the ball and one of the vertical sides of the enclosing
        grid cell that is closer to the hole.

        Args:
            coordinate (tuple(Int, Int)): Coordinate of the ball which should be projected onto one of the
            vertical sides of its enclosing grid cell.

        Returns:
            Bool: Returns the distance of how far the coordinate of the ball is from the top (or bottom) side of its grid cell.
        """

        adj_nodes = self.getAdjNodes(coordinate)
        p0, p1 = self.getClosestSide(adj_nodes['tl'],
                                     adj_nodes['bl'],
                                     adj_nodes['tr'],
                                     adj_nodes['br'],
                                     coordinate)

        try:
            residual = self.calcResidualByIntersection(coordinate, p0, p1)
        except AttributeError:
            # Cannot use intersection for residual calculation so use projection instead
            residual = self.calcResidualByProjection(coordinate, p0, p1)

        # If ball is under the hole (vertically), return residual as it is calculated in the correct direction
        if coordinate[1] > coordinate_hole[1]:
            self.directions.append('Ball Y: UP ')
            return residual

        # Else return distance in the opposite direction
        residual = self.gridlayout.getDistBetweenNodes() - residual

        self.directions.append('BALL Y: DOWN ')
        return residual

    def calcResidualXHole(self, coordinate):
        """
        Calculates the horizontal distance between the coordinate of the hole and its enclosing grid cell.
        Since we can be certain that the ball is positioned left relative to the hole, we only need to focus on the
        distance between the coordinate of the hole and the left side of its enclosing grid cell.

        First it needs to find the line (defined by two points) onto which the ball is projected.
        There are two options to choose from:
            - 1. Top horizontal line defined by the grid points: top left and top right
            - 2. Bottom horizontal line defined by the grid points: bottom left and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.

        Args:
            coordinate (tuple(Int, Int)): Coordinate of the hole which should be projected onto one of the
            horizontal sides of its enclosing grid cell.

        Returns:
            Bool: Returns the distance of how far the coordinate of the hole is from the right side of its grid cell.
        """

        adj_nodes = self.getAdjNodes(coordinate)
        p0, p1 = self.getClosestSide(adj_nodes['tl'],
                                     adj_nodes['tr'],
                                     adj_nodes['bl'],
                                     adj_nodes['br'],
                                     coordinate)

        residual = self.calcResidualByProjection(coordinate, p0, p1)

        self.directions.append('Hole X: LEFT ')

        return residual

    def calcResidualYHole(self, coordinate, coordinate_ball):
        """
        Calculates the vertical distance between the coordinate of the hole and the top (or bottom) side of its enclosing grid cell.

        First it needs to find the line (defined by two points) onto which the ball is projected.
        There are two options to choose from:
            - 1. Right vertical line defined by the grid points: top left and bottom left
            - 2. Left vertical line defined by the grid points: top right and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.

        Depending on where the hole is vertically located relative to the ball (top or bottom), the algorithm will
        return the vertical distance between the coordinate of the hole and one of the vertical sides of the enclosing
        grid cell that is closer to the ball.

        Args:
            coordinate (tuple(Int, Int)): Coordinate of the hole which should be projected onto one of the
            vertical sides of its enclosing grid cell.

        Returns:
            Bool: Returns the distance of how far the coordinate of the hole is from the top (or bottom) side of its grid cell.
        """

        adj_nodes = self.getAdjNodes(coordinate)
        p0, p1 = self.getClosestSide(adj_nodes['bl'],
                                     adj_nodes['tl'],
                                     adj_nodes['br'],
                                     adj_nodes['tr'],
                                     coordinate)

        try:
            residual = self.calcResidualByIntersection(coordinate, p0, p1)
        except AttributeError:
            # Cannot use intersection for residual calculation so use projection instead
            residual = self.calcResidualByProjection(coordinate, p0, p1)

        # If ball is under the hole (vertically), return residual as it is calculated in the correct direction
        if coordinate_ball[1] > coordinate[1]:
            self.directions.append('Hole Y: DOWN ')
            return residual

        # Else return distance in the opposite direction
        residual = self.gridlayout.getDistBetweenNodes() - residual

        self.directions.append('Hole Y: UP ')
        return residual

    def estimateDistance(self, coordinate_hole, coordinate_ball):
        """
        Calculates the distance between the two given coordinates using the predefined grid layout.

        Args:
            coordinate_hole (tuple(Int, Int)): Coordinate of the hole
            coordinate_ball (tuple(Int, Int)): Coordinate of the ball

        Returns:
            Bool: The distance between the golf ball and hole, None if not found
        """

        if coordinate_ball is None or coordinate_hole is None:
            return None

        # Makes sure the ball has the left-most coordinate in order to make further calculations easier. If
        # the hole is on the left side of the ball, the two coordinates are swapped to guarantee the left-most
        # position of the ball. (Swapping of the coordinates does not affect the distance calculation!)
        if coordinate_ball[0] > coordinate_hole[0]:
            coordinate_ball, coordinate_hole = coordinate_hole, coordinate_ball

        # Calc residuals
        x_residual_ball = self.calcResidualXBall(coordinate_ball)
        y_residual_ball = self.calcResidualYBall(coordinate_ball, coordinate_hole)
        x_residual_hole = self.calcResidualXHole(coordinate_hole)
        y_residual_hole = self.calcResidualYHole(coordinate_hole, coordinate_ball)

        residual_total_x = x_residual_ball + x_residual_hole
        residual_total_y = y_residual_ball + y_residual_hole

        cell_ball = self.gridlayout.getContainingCell(coordinate_ball)
        cell_hole = self.gridlayout.getContainingCell(coordinate_hole)

        # Handle special cases like ball and hole are in the same row/column/cell
        if cell_ball.row() == cell_hole.row():
            y_residual_hole = self.gridlayout.getDistBetweenNodes() - y_residual_hole
            residual_total_y = abs(y_residual_ball - y_residual_hole)

        if cell_ball.col() == cell_hole.col():
            x_residual_hole = self.gridlayout.getDistBetweenNodes() - x_residual_hole
            residual_total_x = abs(x_residual_ball - x_residual_hole)

        # Calculate distance
        dist_x, dist_y = self.gridlayout.distCoordinates(coordinate_ball, coordinate_hole)
        a = dist_x * self.gridlayout.getDistBetweenNodes() + residual_total_x
        b = dist_y * self.gridlayout.getDistBetweenNodes() + residual_total_y

        dist = round(math.sqrt(a ** 2 + b ** 2), 2)

        return dist
