import sys
from detection.ObjectDetection import ObjectDetection

# Detect license plate on image provided as a command line argument
det = ObjectDetection("./references/image (3).png")

# Print out result
det.findAceHole()