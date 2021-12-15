import sys
from detection.ObjectDetection import ObjectDetection

# Detect license plate on image provided as a command line argument
det = ObjectDetection("./715-after.png")

# Print out result
det.findAceHole2()