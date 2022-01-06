import sys
from main.DistanceEstimation import DistanceEstimation

estimator = DistanceEstimation()

def test_estimation():
	golf_ball_coordinates = (50, 100)
	hole_coordinates = (541, 205)

	d = estimator.estimateDistance(golf_ball_coordinates, hole_coordinates)
	assert d == 519.3176857432854