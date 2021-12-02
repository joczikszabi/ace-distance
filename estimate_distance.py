import sys
from main.DistanceEstimation import DistanceEstimation

# Make an instance of the LicensePlateDetector class
estimator = DistanceEstimation()

# Detect license plate on image provided as a command line argument
distance = estimator.estimateDistance(int(sys.argv[1]))

# Print out result
print(distance)
