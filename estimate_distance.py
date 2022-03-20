import sys
import cv2
import json
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
det = ObjectDetection(img_before_path, img_after_path, debug_mode=True, out_dir=f"out/alma")
pos_hole = det.findAceHole()
pos_ball = det.findGolfBall()

# Make an instance of the DisnaceEstimation class and run the estimator algorithm
estimator = DistanceEstimation()
dist = estimator.estimateDistance(pos_ball, pos_hole, img_after)

if dist:
	# Create output directory
	out_dir_name = os.path.splitext(os.path.basename(img_after_path))[0]
	out_dir = f"./out/{out_dir_name}"
	os.makedirs(out_dir)

	# Save result image with the distance rendered on it
	cv2.line(img_after, pos_ball, pos_hole, (255, 0, 0), 1)
	cv2.putText(img_after, f"{str(dist)}m", (int((pos_ball[0]+pos_hole[0])/2)-75, int((pos_ball[1]+pos_hole[1])/2-25)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
	cv2.imwrite(f"{out_dir}/result.jpg", img_after)

# Define output object
output = {}
output["distance"] = dist
output["is_hole_detected"] = pos_hole is not None
output["is_ball_detected"] = pos_ball is not None
output["is_distance_calculated"] = dist is not None
output["results_path"] = os.path.abspath(f"{out_dir}/result.jpg") if dist else None

# Print out result
output_json = json.dumps(output)
print(output_json)