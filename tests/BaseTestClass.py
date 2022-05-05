import os
from acedistance.main.ObjectDetection import ObjectDetection


class BaseTestClass:
    def __init__(self, testcase_name):
        self.testcase_name = testcase_name
        self.out_dir = os.path.join(os.path.dirname(__file__), 'test_out', testcase_name)
        self.data_dir = os.path.join(os.path.dirname(__file__), 'test_data', testcase_name)

    def get_detection_object(self, testcase):
        img_before_path = os.path.join(self.data_dir, f'{testcase["img_name"]}-before.png')
        img_after_path = os.path.join(self.data_dir, f'{testcase["img_name"]}-after.png')
        output_path = os.path.join(self.out_dir, testcase['layout'], testcase['img_name'])

        det = ObjectDetection(img_before_path, img_after_path,
                              debug_mode=True,
                              out_dir=output_path,
                              layout_name=testcase['layout'])
        return det

    def get_img_before_path(self, img_name):
        return os.path.join(self.data_dir, f'{img_name}-before.png')

    def get_img_after_path(self, img_name):
        return os.path.join(self.data_dir, f'{img_name}-after.png')

    def get_output_path(self, layout, img_name):
        return os.path.join(self.out_dir, layout, img_name)

