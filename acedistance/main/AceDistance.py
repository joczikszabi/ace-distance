import os
import cv2
import json
import numpy as np
from acedistance.main.Grid import GridLayout
from acedistance.helpers.load import loadConfig
from acedistance.main.ObjectDetection import ObjectDetection
from acedistance.main.DistanceEstimation import DistanceEstimation


class AceDistance:
    def __init__(self, img_before_path, img_after_path, out_dir=None, layout_name=None, debug_mode=None):
        configParser = loadConfig()

        self.img_before_path = img_before_path
        self.img_after_path = img_after_path
        self.out_dir = out_dir if out_dir else configParser['PROGRAM']['DEFAULT_OUTDIR']
        self.result_img_path = f'{self.out_dir}/result.jpg'
        self.result_json_path = f'{self.out_dir}/result.json'
        self.layout_name = layout_name if layout_name else configParser['GRID']['LAYOUT_NAME']
        self.debug_mode = debug_mode if debug_mode else bool(int(configParser['PROGRAM']['DEBUG_MODE']))

        # Properties needed for result
        self.version = configParser['PROGRAM']['VERSION']
        self.pos_hole = None
        self.pos_ball = None
        self.distance = None
        self.error = ''
        self.gridlayout = GridLayout(self.layout_name)

    def run(self):
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
        det = ObjectDetection(img_before_path=self.img_before_path,
                              img_after_path=self.img_after_path,
                              gridlayout=self.gridlayout,
                              out_dir=self.out_dir,
                              debug_mode=self.debug_mode)
        self.pos_hole = det.findAceHole()
        self.pos_ball = det.findGolfBall()

    def runDistanceEstimation(self):
        estimator = DistanceEstimation(gridlayout=self.gridlayout)
        self.distance = estimator.estimateDistance(self.pos_hole, self.pos_ball, cv2.imread(self.img_after_path))

    def defaultOutput(self):
        output = {
            "version": self.version,
            "distance": self.distance,
            "layout_name": self.layout_name,
            "is_hole_detected": self.pos_hole is not None,
            "is_ball_detected": self.pos_ball is not None,
            "results_path": self.result_img_path,
            "img_before_path": self.img_before_path,
            "img_after_path": self.img_after_path,
            "error": self.error
        }

        return output

    def saveResultImage(self):
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
        output = self.defaultOutput()
        output_json = json.dumps(output)

        # Print out result (endpoint is listening to the printed output)
        print(output_json)

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        # Save json for logging purposes
        with open(self.result_json_path, 'w') as f:
            json.dump(output, f)
