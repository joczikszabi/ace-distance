# Distance-Estimation

This is the repository for the AceChallenge distance estimation project where the distance between a golf ball and hole is estimated (in terms of meters) based on two pairs (before shoot / after shoot) images.

The module consists of two main steps:
- Object detection: Using opencv, the golf ball and golf hole is detected on the images
- Distance estimation: Given the coordinates (in pixels) of the golf ball and hole, the distance between the two objects is estimated using a pre-defined layout which maps the pixels on the image to distances in real life (in meters).

### Demo
A demo workflow can be found under the /demo folder. It shows what the output should be for an ideal scenario where the objects (golf ball and hole) are detected accurately, and the distance between them is rendered on the image (result.jpg).
Additionally, a 'result.json' file is exported which includes all meta data necessary for post-processing and debugging.

In the /demo/ball and /demo/hole folders the different masks can be seen that are applied on the images one by one for detecting the golf ball and hole respectively.

![Demo image](demo/result.jpg?raw=true "Demo image")




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