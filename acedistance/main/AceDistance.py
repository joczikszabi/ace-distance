import os
import cv2
import json
import numpy as np
from acedistance.main.Grid import GridLayout
from acedistance.helpers.load import loadConfig
from acedistance.main.ObjectDetection import ObjectDetection
from acedistance.main.DistanceEstimation import DistanceEstimation


class AceDistance:
    def __init__(self, img_before_path, img_after_path, out_dir=None, layout_name=None, debug_mode=False):
        configParser = loadConfig()

        self.img_before_path = img_before_path
        self.img_after_path = img_after_path
        self.out_dir = out_dir if out_dir else configParser['PROGRAM']['DEFAULT_OUTDIR']
        self.result_img_path = f'{self.out_dir}/result.jpg'
        self.result_json_path = f'{self.out_dir}/result.json'
        self.layout_name = layout_name if layout_name else configParser['GRID']['LAYOUT_NAME']
        self.debug_mode = debug_mode

        # Properties needed for result
        self.version = configParser['PROGRAM']['VERSION']
        self.pos_hole = None
        self.pos_ball = None
        self.is_hole_detected = None
        self.is_ball_detected = None
        self.distance = None
        self.error = ''
        self.gridlayout = GridLayout(self.layout_name)

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def run(self):
        """
        Main script that sets up the workflow, connects the different steps (object detection, distance estimation, etc.),
        handles errors and exports output.

        Args:

        Returns:
        """

        if not os.path.isfile(self.img_before_path):
            self.error = f'Image (before) not found on path: {self.img_before_path}'
            self.emitAndSaveOutput()
            return

        if not os.path.isfile(self.img_after_path):
            self.error = f'Image (after) not found on path: {self.img_after_path}'
            self.emitAndSaveOutput()
            return

        try:
            self.runObjectDetection()
            self.runDistanceEstimation()

            if self.distance:
                self.saveResultImage()

        except Exception as e:
            self.error = e.args[0]

        self.emitAndSaveOutput()

    def runObjectDetection(self):
        """
        Wrapper for the object detection algorithm.

        Args:

        Returns:
        """

        det = ObjectDetection(img_before_path=self.img_before_path,
                              img_after_path=self.img_after_path,
                              gridlayout=self.gridlayout,
                              out_dir=self.out_dir,
                              debug_mode=self.debug_mode)

        self.pos_hole = det.findAceHole()
        self.is_hole_detected = self.pos_hole is not None

        self.pos_ball = det.findGolfBall()
        self.is_ball_detected = self.pos_ball is not None

    def runDistanceEstimation(self):
        """
        Wrapper for the distance estimation algorithm.

        Args:

        Returns:
        """

        estimator = DistanceEstimation(gridlayout=self.gridlayout)
        self.distance = estimator.estimateDistance(coordinate_hole=self.pos_hole, coordinate_ball=self.pos_ball)

    def defaultOutput(self):
        """
        Defines and returns the default output format.

        Args:

        Returns:
            Output of the ace-distance algorithm
        """

        output = {
            "version": self.version,
            "distance": self.distance,
            "layout_name": self.layout_name,
            "is_hole_detected": self.is_hole_detected,
            "is_ball_detected": self.is_ball_detected,
            "results_path": self.result_img_path,
            "img_before_path": self.img_before_path,
            "img_after_path": self.img_after_path,
            "error": self.error
        }

        return output

    def saveResultImage(self):
        """
        Renders the coordinates of the golf hole and ball on the image along with the distance between them
        and exports the image.

        Args:

        Returns:
        """

        img = cv2.imread(self.img_after_path)
        cv2.line(img, self.pos_ball, self.pos_hole, (255, 0, 0), 1)

        # Find midsection of distance line and shift label to the top-left by 75 and 25 pixels
        label_position = np.sum([self.pos_hole, self.pos_ball, [-75, -25]], 0) / 2
        label_position = label_position.astype(int)
        cv2.putText(img=img,
                    text=f'{str(self.distance)}m',
                    org=tuple(label_position),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(255, 0, 0),
                    thickness=2)
        cv2.imwrite(self.result_img_path, img)

    def emitAndSaveOutput(self):
        """
        Wrapper for exporting the ace-distance output in a json form (and prints it on the terminal as the backend
        listens to it)

        Args:

        Returns:
        """

        output = self.defaultOutput()
        output_json = json.dumps(output)

        # Print out result (endpoint is listening to the printed output)
        print(output_json)

        with open(self.result_json_path, 'w') as f:
            json.dump(output, f)
