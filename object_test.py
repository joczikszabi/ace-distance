import sys
from detection.ObjectDetection import ObjectDetection

# Detect license plate on image provided as a command line argument
det = ObjectDetection("./699-after.png")
det.findAceHole2()

det = ObjectDetection("./715-after.png")
det.findAceHole2()

det = ObjectDetection("./753-before.png")
det.findAceHole2()

det = ObjectDetection("./763-after.png")
det.findAceHole2()

det = ObjectDetection("./793-Before.png")
det.findAceHole2()