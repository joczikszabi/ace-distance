# Distance-Estimation

This is the repository for the AceChallenge distance estimation project where we estimate the distance between the golf ball and hole.

# Installing (Linux / MacOS)
#### Run install script
The install script creates a new conda environement based on the configuration given in environment.yml. If the environment already exists, it will remove it first. To install the necessary python packages, use:
```bash
./install.sh
```

# Testing
To test out the algorithm, go to the test folder and run
```bash
python object_detection_test.py
```
After the script is finished, the results can be found under /test/results/ directory


# Usage
The main algorithm can be run using estimate_distance.py. The script requires the path of two images (one before and after the shot) as arguments. An example usage can be the following:
```
python estimate_distance.py "test/data/708-before.png" "test/data/708-after.png"
```