import os
import json
import shutil
import pytest

import estimate_distance
from main.DistanceEstimation import DistanceEstimation
from main.ObjectDetection import ObjectDetection


def get_testcases():
    # Loop through the different grid layouts and load their corresponding test data and expected results
    #
    # Expected results contain the following data of an image:
    # - img_name: Name of the image
    # - is_hole_visible: Is the Ace hole visible on the image?
    # - is_ball_visible: Is the golf ball visible on the image?
    test_data_dir = './test_data/object_detection_test'
    test_cases = []
    for subdir, dirs, files in os.walk(test_data_dir):
        for dir in dirs:
            expected_json = os.path.join(subdir, dir, 'test_cases.json')
            if not os.path.isfile(expected_json):
                continue

            with open(expected_json, 'r') as f:
                data = json.load(f)
                test_cases += data['test_cases']

    return test_cases


class TestObjectDetection:
    test_dir = './test_out'
    out_dir = f'{test_dir}/object_detection_test'
    test_data_dir = './test_data/object_detection_test'
    estimator = DistanceEstimation()

    # Setup method
    @classmethod
    def setup_class(cls):
        print('\n\n#####RUNNING SETUP FUNCTION#####')
        print('Creating temp directories..')

        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        os.makedirs(cls.test_dir)

        testcases = get_testcases()
        for testcase in testcases:
            testcase_path = os.path.join(cls.out_dir, testcase['layout'])
            if not os.path.exists(testcase_path):
                os.makedirs(testcase_path)
            os.makedirs(os.path.join(testcase_path, testcase['img_name']))

        print('Temp directories created successfully!')

    @pytest.mark.parametrize("testcase", get_testcases())
    def test_hole_detection(self, testcase):
        # Run distance estimation script and check if hole was detected correctly or not
        layout_path = os.path.join(self.test_data_dir, testcase['layout'])
        img_before_path = os.path.join(layout_path, f'{testcase["img_name"]}-before.png')
        img_after_path = os.path.join(layout_path, f'{testcase["img_name"]}-after.png')
        output_path = os.path.join(self.out_dir, testcase["layout"], testcase["img_name"])

        det = ObjectDetection(img_before_path, img_after_path,
                              debug_mode=True,
                              out_dir=output_path,
                              grid_layout=testcase['layout'])
        pos_hole = det.findAceHole()

        assert (pos_hole is not None) == testcase["is_hole_detected"]

    @pytest.mark.parametrize("testcase", get_testcases())
    def test_ball_detection(self, testcase):
        # Run distance estimation script and check if hole was detected correctly or not
        layout_path = os.path.join(self.test_data_dir, testcase['layout'])
        img_before_path = os.path.join(layout_path, f'{testcase["img_name"]}-before.png')
        img_after_path = os.path.join(layout_path, f'{testcase["img_name"]}-after.png')
        output_path = os.path.join(self.out_dir, testcase["layout"], testcase["img_name"])

        det = ObjectDetection(img_before_path, img_after_path,
                              debug_mode=True,
                              out_dir=output_path,
                              grid_layout=testcase['layout'])
        pos_ball = det.findGolfBall()

        assert (pos_ball is not None) == testcase["is_ball_detected"]

    @pytest.mark.parametrize("testcase", get_testcases())
    def test_result_exported(self, testcase):
        # If both the hole and the ball is visible on the image, check if the distance
        # between them has been estimated based on the returned value ad whether or not the
        # image 'distance_estimation.jpg' exists

        # Run distance estimation script and check if result is calculated and output image is exported
        layout_path = os.path.join(self.test_data_dir, testcase['layout'])
        img_before_path = os.path.join(layout_path, f'{testcase["img_name"]}-before.png')
        img_after_path = os.path.join(layout_path, f'{testcase["img_name"]}-after.png')
        output_path = os.path.join(self.out_dir, testcase["layout"], testcase["img_name"])
        estimate_distance.main(img_before_path, img_after_path, output_path, testcase['layout'])

        if testcase['is_hole_detected'] and testcase['is_ball_detected']:
            assert os.path.isfile(
                f'{self.out_dir}/{testcase["layout"]}/{testcase["img_name"]}/result.jpg')  # Check if image is exported
            assert os.path.isfile(
                f'{self.out_dir}/{testcase["layout"]}/{testcase["img_name"]}/results.json')  # Check if json file is exported

        print('---------------------------------')
