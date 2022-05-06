import math
import cv2
import numpy as np
from scipy.spatial import distance


class DistanceEstimation:
    def __init__(self, gridlayout):
        self.gridlayout = gridlayout

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

        return adj_nodes

    def point_on_line(self, a, b, p):
        ap = p - a
        ab = b - a
        t = np.dot(ap, ab) / np.dot(ab, ab)
        # if you need the the closest point belonging to the segment
        t = max(0, min(1, t))
        projection = a + t * ab

        cv2.circle(self.img, (int(projection[0]), int(projection[1])), 2, (255, 0, 255), -1)

        return t, projection

    def shortest_distance(self, point, p0, p1):
        a = p0[1] - p1[1]
        b = p1[0] - p0[0]
        c = p0[0] * p1[1] - p0[1] * p1[0]

        d = abs((a * point[0] + b * point[1] + c)) / (math.sqrt(a * a + b * b))
        print(f"Perpendicular distance is: {d}")

    def projectCoordinate(self, coordinate, p0, p1):
        # Projects the given coordinates on perpendicular basis vectors
        # Ref: https://stackoverflow.com/questions/61341712/calculate-projected-point-location-x-y-on-given-line-startx-y-endx-y

        adj_nodes = self.getAdjNodes(coordinate)
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

        l2 = np.sum((p0 - p1) ** 2)
        t = np.sum((coordinate - p0) * (p1 - p0)) / l2

        projection = p0 + t * (p1 - p0)
        cv2.circle(self.img, (int(projection[0]), int(projection[1])), 2, (255, 0, 255), -1)
        return t, projection

    def calcResidual(self, coordinate, p0, p1):
        # Calculates residuals in terms of meters

        # Project coordinates
        # t, projection = self.projectCoordinate(coordinate=coordinate, p0=np.array(p0), p1=np.array(p1))
        c = self.gridlayout.getContainingCell(coordinate)
        t, projection = self.point_on_line(np.array(p0), np.array(p1), coordinate)
        print(f't: {t}')
        residual = self.gridlayout.getDistBetweenNodes() * t

        self.shortest_distance(coordinate, p0, p1)

        return residual

    def getAverage(self, p0, p1):
        p0 = np.array(p0)
        p1 = np.array(p1)

        avg = (p0 + p1) / 2
        return avg

    def getClosestSide(self, p0, p1, p2, p3, coordinate):
        p0 = np.array(p0)
        p1 = np.array(p1)
        p2 = np.array(p2)
        p3 = np.array(p3)
        coordinate = np.array(coordinate)

        avg1 = self.getAverage(p0, p1)
        avg2 = self.getAverage(p2, p3)

        if distance.euclidean(avg1, coordinate) < distance.euclidean(avg2, coordinate):
            return p0, p1

        return p2, p3

    def estimateDistance(self, coordinate_ball, coordinate_hole, img):
        self.img = img

        if coordinate_ball is None or coordinate_hole is None:
            return None

        # Make sure ball has the left-most coordinate (makes calculations easier)
        # swap coordinates if hole is on the left (it makes no difference from the distance calculation point of view)
        if coordinate_ball[0] > coordinate_hole[0]:
            coordinate_ball, coordinate_hole = coordinate_hole, coordinate_ball

        adj_nodes_ball = self.getAdjNodes(coordinate_ball)
        adj_nodes_hole = self.getAdjNodes(coordinate_hole)

        # Calc residuals
        x_ball_p0, x_ball_p1 = self.getClosestSide(adj_nodes_ball['tr'],
                                                   adj_nodes_ball['tl'],
                                                   adj_nodes_ball['bl'],
                                                   adj_nodes_ball['br'],
                                                   coordinate_ball)

        y_ball_p0, y_ball_p1 = self.getClosestSide(adj_nodes_ball['tr'],
                                                   adj_nodes_ball['br'],
                                                   adj_nodes_ball['tl'],
                                                   adj_nodes_ball['bl'],
                                                   coordinate_ball)

        x_hole_p0, x_hole_p1 = self.getClosestSide(adj_nodes_hole['tl'],
                                                   adj_nodes_hole['tr'],
                                                   adj_nodes_hole['bl'],
                                                   adj_nodes_hole['br'],
                                                   coordinate_hole)

        y_hole_p0, y_hole_p1 = self.getClosestSide(adj_nodes_hole['br'],
                                                   adj_nodes_hole['tr'],
                                                   adj_nodes_hole['bl'],
                                                   adj_nodes_hole['tl'],
                                                   coordinate_hole)

        res_x_ball = self.calcResidual(coordinate_ball, x_ball_p0, x_ball_p1)
        res_y_ball = self.calcResidual(coordinate_ball, y_ball_p0, y_ball_p1)
        res_x_hole = self.calcResidual(coordinate_hole, x_hole_p0, x_hole_p1)
        res_y_hole = self.calcResidual(coordinate_hole, y_hole_p0, y_hole_p1)

        if coordinate_hole[1] < coordinate_ball[1]:
            res_y_hole = self.gridlayout.getDistBetweenNodes() - res_y_hole
        else:
            res_y_ball = self.gridlayout.getDistBetweenNodes() - res_y_ball

        print("Projecting on x (ball)")
        print(f'Coordinate: {coordinate_ball}')
        print(f'residual: {res_x_ball}')

        print("Projecting on y (ball)")
        print(f'Coordinate: {coordinate_ball}')
        print(f'residual: {res_y_ball}')

        print("Projecting on x (hole)")
        print(f'Coordinate: {coordinate_hole}')
        print(f'residual: {res_x_hole}')

        print("Projecting on y (hole)")
        print(f'Coordinate: {coordinate_hole}')
        print(f'residual: {res_y_hole}')

        dist_x, dist_y = self.gridlayout.getDistBetweenCells(coordinate_ball, coordinate_hole)
        a = dist_x * self.gridlayout.getDistBetweenNodes()# + (res_x_ball + res_x_hole)
        b = dist_y * self.gridlayout.getDistBetweenNodes()# + (res_y_ball + res_y_hole)

        dist = round(math.sqrt(a ** 2 + b ** 2), 2)

        return dist
