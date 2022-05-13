# Distance-Estimation

This is the repository for the AceChallenge distance estimation project where we estimate the distance between the golf ball and hole.

# Installing (Linux / MacOS)
#### Run install script
The install script creates a new conda environment based on the configuration given in environment.yml. If the environment already exists, it will remove it first. To install the necessary python packages, use:
```bash
./setup.sh
```

# Usage
The main algorithm can be run using estimate_distance.py. The script requires the path of two images (one before and after the shot) as arguments. An example usage can be the following:
```
python estimate_distance.py "test/data/708-before.png" "test/data/708-after.png"
```

To see every optional parameter, use:
```
python estimate_distance.py --help
```

# Testing
Pytest is used for testing the algorithm. Run pytest which automatically detects and runs all test functions
```bash
pytest
```

To run tests in debug mode with printed messages displayed, use
```bash
pytest -s 
```

After the script is finished, the results can be found under /test_results

# Deploy
In order to deploy the module for use on production serve, use the deploy script as follows:
```
python deploy.py
```
The deployed version will be a minimized version of the repository with only the neccessary modules and packages included