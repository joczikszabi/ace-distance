import sys
import cv2
import os.path

from helpers.plot_grid import plot_grid
from main.ObjectDetection import ObjectDetection
from main.DistanceEstimation import DistanceEstimation

img_before_path = sys.argv[1]
img_after_path 	= sys.argv[2]

if os.path.isfile(img_before_path):
	img_before = cv2.imread(img_before_path)
else:
	exit(f"Image (before) not found on path: {img_before_path}")

if os.path.isfile(img_after_path):
	img_after = cv2.imread(img_after_path)
else:
	exit(f"Image (after) not found on path: {img_after_path}")

# Make an instance of the ObjectDetection classes and run the detection algorithm
det = ObjectDetection(img_before_path, img_after_path, debug_mode=False)
pos_hole = det.findAceHole()
pos_ball = det.findGolfBall()

# Make an instance of the DisnaceEstimation class and run the estimator algorithm
estimator = DistanceEstimation()

if pos_hole is not None and pos_ball is not None:
	dist = estimator.estimateDistance(pos_ball, pos_hole)
	print(dist)

else:
	print(None)