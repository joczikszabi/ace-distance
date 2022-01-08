import os
import sys
import cv2
import shutil
import pytest

# For top level import
sys.path.append("..")
print(os.getcwd())
from helpers.plot_grid import plot_grid
from main.ObjectDetection import ObjectDetection
from main.DistanceEstimation import DistanceEstimation


class TestObjectDetection():
	tmp_dir = f"./test_results"
	estimator = DistanceEstimation()

	# Format: (IMG_NAME, IS_HOLE_VISIBLE, IS_BALL_VISIBLE)
	#
	# Parameters:
	# - IMG_NAME: Name of the image
	# - IS_HOLE_VISIBLE: Is the Ace hole visible on the image?
	# - IS_BALL_VISIBLE: Is the golf ball visible on the image?
	test_cases = [
		('699', True, False),
		('708', True, True),
		('715', True, True),
		('753', True, False),
		('763', True, True),
		('768', True, True),
		('770', True, True),
	]


	# Setup method
	@classmethod
	def setup_class(cls):
		print('\n\n#####RUNNING SETUP FUNCTION#####')
		print('Creating temp directory..')

		tmp_dir = f"./test_results"
		if os.path.exists(tmp_dir):
			shutil.rmtree(tmp_dir)
		os.makedirs(tmp_dir)

		print('Temp directory created successfully!')


	'''
	Test functions below
	'''
	@pytest.mark.parametrize(('img_name', 'is_hole_visible', 'is_ball_visible'), test_cases)
	def test_hole_detection(self, img_name, is_hole_visible, is_ball_visible):
		# Check if hole was detected correctly or not
		assert os.path.isfile(f"{self.tmp_dir}/{img_name}/hole/6result.jpg") == is_hole_visible


	@pytest.mark.parametrize(('img_name', 'is_hole_visible', 'is_ball_visible'), test_cases)
	def test_ball_detection(self, img_name, is_hole_visible, is_ball_visible):
		# Check if hole was detected correctly or not
		assert os.path.isfile(f"{self.tmp_dir}/{img_name}/ball/6result.jpg") == is_ball_visible


	@pytest.mark.parametrize(('img_name', 'is_hole_visible', 'is_ball_visible'), test_cases)
	def test_result_exported(self, img_name, is_hole_visible, is_ball_visible):
		# If both the hole and the ball is visible on the image, check if the distance
		# between them has been estimated based on whether or not the 
		# image 'distance_estimation.jpg' exists or not

		if is_hole_visible and is_ball_visible:
			assert os.path.isfile(f"{self.tmp_dir}/{img_name}/distance_estimation.jpg")

		print('---------------------------------')

	'''
	End of test functions
	------------------------------------------------------------------
	'''

	@pytest.fixture(scope="class", autouse=True)
	def runTests(self):
		print('\n\n#####RUNNING ALGORITHM ON TEST IMAGES#####')
		for test_case in self.test_cases:
			img_name = test_case[0]

			img_before_path = f"./data/{img_name}-before.png"
			img_after_path 	= f"./data/{img_name}-after.png"

			img_before = cv2.imread(img_before_path)
			img_after = cv2.imread(img_after_path)

			# Create directory for outputs
			out_dir = f"{self.tmp_dir}/{img_name}"
			if not os.path.exists(out_dir):
				os.makedirs(out_dir)

			# Save image and grid layout
			cv2.imwrite(f"{out_dir}/0image_orig_before.jpg", img_before)
			cv2.imwrite(f"{out_dir}/0image_orig_after.jpg", img_after)

			img_grid = plot_grid(img_before, self.estimator.grid)
			cv2.imwrite(f"{out_dir}/1image_grid.jpg", img_after)


			# Run distance estimation algorith
			print(f"\nCurrent image: {img_name}")
			det = ObjectDetection(img_before_path, img_after_path, True, out_dir)
			pos_hole = det.findAceHole()
			pos_ball = det.findGolfBall()


			# Print golf hole position
			if pos_hole:
				print(f"Golf hole located at pixel coordinates: {pos_hole}")
			else:
				print(f"Golf hole could not be located on image!")

			# Print golf ball position
			if pos_ball:
				print(f"Golf ball located at pixel coordinates: {pos_ball}")
			else:
				print(f"Golf ball could not be located on image!")


			if pos_hole is not None and pos_ball is not None:
				# Display the coordinates on the image window
				font = cv2.FONT_HERSHEY_SIMPLEX
				cv2.line(img_after, pos_ball, pos_hole, (255, 0, 0), 1)

				# Estimate distance
				dist = self.estimator.estimateDistance(pos_ball, pos_hole)

				if dist is not None:
					dist = round(dist, 2)
					print(f"Estimated distance between ball and hole: {dist} meter(s)")
					cv2.putText(img_after, f"{str(dist)}m", (int((pos_ball[0]+pos_hole[0])/2)-75, int((pos_ball[1]+pos_hole[1])/2-25)), font, 1, (255, 0, 0), 2)
				
				else:
					cv2.putText(img_after, f"Out of grid", (int((pos_ball[0]+pos_hole[0])/2)-125, int((pos_ball[1]+pos_hole[1])/2-25)), font, 1, (255, 0, 0), 2)
				
				cv2.imwrite(f"{out_dir}/distance_estimation.jpg", img_after)
				print(f"Image saved at: {out_dir}/3distance_estimation.jpg")

		print('Distance estimation algorithm finished running on all test images!')
