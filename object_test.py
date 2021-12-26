import os
import sys
import cv2
from helpers.plot_grid import plot_grid
from detection.ObjectDetection import ObjectDetection
from main.DistanceEstimation import DistanceEstimation


def runTest(img_name):
	img_before_path = f"{img_name}-before.png"
	img_after_path 	= f"{img_name}-after.png"

	img_before = cv2.imread(img_before_path)
	img_after = cv2.imread(img_after_path)
	img_after_orig = img_after.copy()

	# Create directory for outputs
	out_dir = f"./tmp/{img_name}"
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	# Save image and grid layout
	cv2.imwrite(f"{out_dir}/0image_orig_before.jpg", img_before)
	cv2.imwrite(f"{out_dir}/0image_orig_after.jpg", img_after_orig)

	img_grid = plot_grid(img_after_orig, estimator.grid)
	cv2.imwrite(f"{out_dir}/1image_grid.jpg", img_after_orig)

	# Detect license plate on image provided as a command line argument
	print(f"\nCurrent image: {img_name}")
	det = ObjectDetection(f"./{img_after_path}")
	pos_hole = det.findAceHole2(out_dir)
	pos_ball = det.findGolfBall(img_before_path, out_dir)

	if pos_hole is not None and pos_ball is not None:
		# displaying the coordinates on the image window
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.circle(img_after, pos_hole, 5, (0, 255, 255), -1)
		cv2.circle(img_after, pos_ball, 5, (255, 0, 0), -1)
		cv2.line(img_after, pos_ball, pos_hole, (255, 0, 0), 1)

		# Do distance estimation
		dist = estimator.estimateDistance(pos_ball, pos_hole)

		if dist is not None:
			dist = round(dist, 2)
			print(f"Golf ball located at pixel coordinates: ({pos_ball})")
			print(f"Golf hole located at pixel coordinates: ({pos_hole})")
			print(f"Estimated distance between ball and hole: {dist} meter(s)\n")

			# displaying the coordinates on the image window
			cv2.putText(img_after, f"{str(dist)}m", (int((pos_ball[0]+pos_hole[0])/2)-75, int((pos_ball[1]+pos_hole[1])/2-25)), font, 1, (255, 0, 0), 2)
		else:
			cv2.putText(img_after, f"Out of grid", (int((pos_ball[0]+pos_hole[0])/2)-125, int((pos_ball[1]+pos_hole[1])/2-25)), font, 1, (255, 0, 0), 2)
		
		cv2.imwrite(f"{out_dir}/distance_estimation.jpg", img_after)
		print(f"Image saved at: {out_dir}/3distance_estimation.jpg\n")

# Cases
estimator = DistanceEstimation()

imgs = ["699", "708", "715", "753", "763", "768", "770"]
for img in imgs:
	runTest(img)