import math
import cv2
import numpy as np
from shapely.geometry import LineString


class DistanceEstimation:
    def __init__(self, gridlayout):
        self.gridlayout = gridlayout
        self.directions = []

    def getAdjNodes(self, coordinate):
        cell = self.gridlayout.getContainingCell(coordinate)

        if not cell:
            raise ValueError('Position out of grid!')

        points = cell.getPoints()
        adj_nodes = {
            'tl': points[0],
            'tr': points[1],
            'br': points[2],
            'bl': points[3]
        }

        """
        cv2.putText(self.img, 'tl', (int(adj_nodes['tl'][0]) - 10, int(adj_nodes['tl'][1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['tl'][0], adj_nodes['tl'][1]), 2, (100, 200, 0), -1)

        cv2.putText(self.img, 'tr', (int(adj_nodes['tr'][0]) + 10, int(adj_nodes['tr'][1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['tr'][0], adj_nodes['tr'][1]), 2, (100, 200, 0), -1)

        cv2.putText(self.img, 'br', (int(adj_nodes['br'][0]) + 10, int(adj_nodes['br'][1]) + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['br'][0], adj_nodes['br'][1]), 2, (100, 200, 0), -1)

        cv2.putText(self.img, 'bl', (int(adj_nodes['bl'][0]) - 10, int(adj_nodes['bl'][1]) + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['bl'][0], adj_nodes['bl'][1]), 2, (100, 200, 0), -1)
        """
        return adj_nodes

    def point_on_line(self, a, b, p):
        ap = p - a
        ab = b - a
        t = np.dot(ap, ab) / np.dot(ab, ab)
        # if you need the the closest point belonging to the segment
        t = max(0, min(1, t))
        projection = a + t * ab

        # cv2.circle(self.img, (int(projection[0]), int(projection[1])), 2, (255, 0, 255), -1)

        return t, projection

    def shortest_distance(self, point, p0, p1):
        """Calculates the shortest distance between a point and a line defined by two points.
        The shortest distance is calculated using a perpendicular projection.

        Args:
            point (tuple(int, int)): Point
            p0 (tuple(int, int)): First point on the line
            p1 (tuple(int, int)): Second point on the line

        Returns:
            float: Shortest distance between point and line
        """
        a = p0[1] - p1[1]
        b = p1[0] - p0[0]
        c = p0[0] * p1[1] - p0[1] * p1[0]

        d = abs((a * point[0] + b * point[1] + c)) / (math.sqrt(a * a + b * b))
        # print(f"Perpendicular distance is: {d}")

        return d

    def projectCoordinate(self, coordinate, p0, p1):
        # Projects the given coordinates on perpendicular basis vectors
        # Ref: https://stackoverflow.com/questions/61341712/calculate-projected-point-location-x-y-on-given-line-startx-y-endx-y

        adj_nodes = self.getAdjNodes(coordinate)
        '''
        cv2.putText(self.img, 'tl', (int(adj_nodes['tl'][0]) - 10, int(adj_nodes['tl'][1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['tl'][0], adj_nodes['tl'][1]), 2, (100, 200, 0), -1)

        cv2.putText(self.img, 'tr', (int(adj_nodes['tr'][0]) + 10, int(adj_nodes['tr'][1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['tr'][0], adj_nodes['tr'][1]), 2, (100, 200, 0), -1)

        cv2.putText(self.img, 'br', (int(adj_nodes['br'][0]) + 10, int(adj_nodes['br'][1]) + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['br'][0], adj_nodes['br'][1]), 2, (100, 200, 0), -1)

        cv2.putText(self.img, 'bl', (int(adj_nodes['bl'][0]) - 10, int(adj_nodes['bl'][1]) + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.circle(self.img, (adj_nodes['bl'][0], adj_nodes['bl'][1]), 2, (100, 200, 0), -1)
        '''

        l2 = np.sum((p0 - p1) ** 2)
        t = np.sum((coordinate - p0) * (p1 - p0)) / l2

        projection = p0 + t * (p1 - p0)
        # cv2.circle(self.img, (int(projection[0]), int(projection[1])), 2, (255, 0, 255), -1)
        return t, projection

    def calcResidualByProjection(self, coordinate, p0, p1):
        # Calculates residuals in terms of meters using projection

        # Project coordinates
        # t, projection = self.projectCoordinate(coordinate=coordinate, p0=p0, p1=p1)
        t, projection = self.point_on_line(np.array(p0), np.array(p1), coordinate)
        # print(f't: {t}')
        residual = self.gridlayout.getDistBetweenNodes() * t

        # print(self.shortest_distance(coordinate, p0, p1))

        return residual

    def calcResidualByIntersection(self, coordinate, p0, p1):
        """ Calc residual using simple intersection"""

        adj_nodes = self.getAdjNodes(coordinate)

        grid_vertical_sideline = LineString([p0, p1])
        max_x = max([v[0] for v in adj_nodes.values()])
        horizontal_line = LineString([(0, coordinate[1]), (max_x, coordinate[1])])
        intersected_point = grid_vertical_sideline.intersection(horizontal_line)
        intersected_point = np.array([intersected_point.x, intersected_point.y])
        residual = self.calcResidualByProjection(intersected_point, p0, p1)

        return residual

    def getClosestSide(self, p0, p1, p2, p3, coordinate):
        '''
        p0 = np.array(p0)
        p1 = np.array(p1)
        p2 = np.array(p2)
        p3 = np.array(p3)
        coordinate = np.array(coordinate)

        avg1 = (p0 + p1) / 2
        avg2 = (p2 + p3) / 2

        if distance.euclidean(avg1, coordinate) < distance.euclidean(avg2, coordinate):
            return p0, p1

        return p2, p3
        '''

        d1 = self.shortest_distance(coordinate, p0, p1)
        d2 = self.shortest_distance(coordinate, p2, p3)

        if d1 < d2:
            return p0, p1

        return p2, p3

    def fixPositionsHorizontally(self, coordinate_ball, coordinate_hole):
        """Makes sure the ball has the left-most coordinate in order to makes further calculations easier. If
        the hole is on the left side of the ball, the two coordinates are swapped to guarantee the left-most
        position of the ball. (Swapping of the coordinates does not affect the distance calculation!)

        Args:
            coordinate_ball (tuple(int, int)): Coordinate of the ball
            coordinate_hole (tuple(int, int)): Coordinate of the hole

        Returns:
            tuple(int, int): Returns the coordinate of the ball and the hole in the right order
        """

        if coordinate_ball[0] > coordinate_hole[0]:
            coordinate_ball, coordinate_hole = coordinate_hole, coordinate_ball

        return coordinate_ball, coordinate_hole

    def calcResidualXBall(self, coordinate):
        """ TODO: CONVERT TO GOOGLE DOCSTRING FORMAT
        Find the line (defined by two points) onto which the ball is projected horizontally.
        There are two options to choose from:
            - 1. Top horizontal line defined by the grid points: top left and top right
            - 2. Bottom horizontal line defined by the grid points: bottom left and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.
        """

        adj_nodes = self.getAdjNodes(coordinate)
        p0, p1 = self.getClosestSide(adj_nodes['tr'],
                                     adj_nodes['tl'],
                                     adj_nodes['br'],
                                     adj_nodes['bl'],
                                     coordinate)

        residual = self.calcResidualByProjection(coordinate, p0, p1)

        self.directions.append('Ball X: RIGHT ')

        return residual

    def calcResidualYBall(self, coordinate, coordinate_hole):
        """ TODO: CONVERT TO GOOGLE DOCSTRING FORMAT
        Find the line (defined by two points) onto which the ball is projected horizontally.
        There are two options to choose from:
            - 1. Top horizontal line defined by the grid points: top left and top right
            - 2. Bottom horizontal line defined by the grid points: bottom left and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.
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
        """ TODO: CONVERT TO GOOGLE DOCSTRING FORMAT
        Find the line (defined by two points) onto which the hole is projected horizontally.
        There are two options to choose from:
            - 1. Top horizontal line defined by the grid points: top left and top right
            - 2. Bottom horizontal line defined by the grid points: bottom left and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.
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
        """ TODO: CONVERT TO GOOGLE DOCSTRING FORMAT
        Find the line (defined by two points) onto which the ball is projected horizontally.
        There are two options to choose from:
            - 1. Top horizontal line defined by the grid points: top left and top right
            - 2. Bottom horizontal line defined by the grid points: bottom left and bottom right
        The line 'closest' to the coordinate is chosen so the project onto it can be more accurate.
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

    def estimateDistance(self, coordinate_ball, coordinate_hole, img):
        self.img = img

        if coordinate_ball is None or coordinate_hole is None:
            return None

        # Fix position (horizontally)
        coordinate_ball, coordinate_hole = self.fixPositionsHorizontally(coordinate_hole, coordinate_ball)

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
        # ...
        if cell_ball.row() == cell_hole.row():
            y_residual_hole = self.gridlayout.getDistBetweenNodes() - y_residual_hole
            residual_total_y = abs(y_residual_ball - y_residual_hole)

        if cell_ball.col() == cell_hole.col():
            x_residual_hole = self.gridlayout.getDistBetweenNodes() - x_residual_hole
            residual_total_x = abs(x_residual_ball - x_residual_hole)

        '''
        print("Projecting on x (ball)")
        print(f'Coordinate: {coordinate_ball}')
        print(f'residual: {x_residual_ball}')

        print("Projecting on y (ball)")
        print(f'Coordinate: {coordinate_ball}')
        print(f'residual: {y_residual_ball}')

        print("Projecting on x (hole)")
        print(f'Coordinate: {coordinate_hole}')
        print(f'residual: {x_residual_hole}')

        print("Projecting on y (hole)")
        print(f'Coordinate: {coordinate_hole}')
        print(f'residual: {y_residual_hole}')

        print(f'Residual total (x): {residual_total_x}')
        print(f'Residual total (y): {residual_total_y}')
        '''

        dist_x, dist_y = self.gridlayout.distCoordinates(coordinate_ball, coordinate_hole)
        a = dist_y * self.gridlayout.getDistBetweenNodes() + residual_total_x
        b = dist_x * self.gridlayout.getDistBetweenNodes() + residual_total_y

        # [print(x) for x in self.directions]

        dist = round(math.sqrt(a ** 2 + b ** 2), 2)

        return dist
