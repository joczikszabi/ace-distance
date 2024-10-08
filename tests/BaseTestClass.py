import os
from acedistance.main.Grid import GridLayout
from acedistance.main.ObjectDetection import ObjectDetection
from acedistance.main.DistanceEstimation import DistanceEstimation


class BaseTestClass:
    def __init__(self, testcase_name):
        self.testcase_name = testcase_name
        self.out_dir = os.path.join(os.path.dirname(__file__), 'test_out', testcase_name)
        self.data_dir = os.path.join(os.path.dirname(__file__), 'test_data', testcase_name)

    def get_detection_object(self, testcase):
        img_before_path = os.path.join(self.data_dir, f'{testcase["img_name"]}-before.png')
        img_after_path = os.path.join(self.data_dir, f'{testcase["img_name"]}-after.png')
        output_path = os.path.join(self.out_dir, testcase['layout'], testcase['img_name'])
        gridlayout = GridLayout(testcase['layout'])

        det = ObjectDetection(img_before_path=img_before_path,
                              img_after_path=img_after_path,
                              gridlayout=gridlayout,
                              out_dir=output_path,
                              debug_mode=True)
        return det

    def get_distance_estimation_object(self, layout):
        gridlayout = GridLayout(layout)
        estimator = DistanceEstimation(gridlayout=gridlayout)

        return estimator

    def get_img_before_path(self, img_name):
        return os.path.join(self.data_dir, f'{img_name}-before.png')

    def get_img_after_path(self, img_name):
        return os.path.join(self.data_dir, f'{img_name}-after.png')

    def get_output_path(self, layout, img_name):
        return os.path.join(self.out_dir, layout, img_name)

