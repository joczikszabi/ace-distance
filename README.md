# Distance-Estimation

This is the repository for the AceChallenge distance estimation project where the distance between a golf ball and hole
is estimated (in terms of meters) based on two pairs (before shoot / after shoot) images.

The module consists of two main steps:

- Object detection: Using opencv, the golf ball and golf hole is detected on the images
- Distance estimation: Given the coordinates (in pixels) of the golf ball and hole, the distance between the two objects
  is estimated using a pre-defined layout which maps the pixels on the image to distances in real life (in meters).

### Demo

A demo workflow can be found under the /demo folder. It shows what the output should be for an ideal scenario where the
objects (golf ball and hole) are detected accurately, and the distance between them is rendered on the image (
result.jpg). Additionally, a 'result.json' file is exported which includes all meta data necessary for post-processing
and debugging.

In the /demo/ball and /demo/hole folders the different masks can be seen that are applied on the images one by one for
detecting the golf ball and hole respectively.

![Demo image](demo/result.jpg?raw=true "Demo image")

# Installing (Linux / MacOS)

#### Run install script

The install script creates a new conda environment based on the configuration given in environment.yml. If the
environment already exists, it will remove it first. To install the necessary python packages, use:

```bash
./setup.sh
```

# Usage

The main algorithm can be run using estimate_distance.py. The script requires the path of two images (one before and
after the shot) as arguments. An example usage can be the following:

```
python estimate_distance.py "test/data/708-before.png" "test/data/708-after.png"
```

To see every optional parameter, use:

```
python estimate_distance.py --help
```

# Testing

Pytest is used for testing the algorithm. Run pytest which automatically detects and runs all test functions:

```bash
pytest
```

To run tests in debug mode with printed messages displayed, use:

```bash
pytest -s
```

After the script is finished, the results can be found under /test_results.

### Preparing test cases

In order to prepare the images (expected values) for object detection, use

```bash
cd tests/helpers && python prepare_dataset_for_object_detection.py
```

It will go through all images in tests/test_data/object_detection by default but additionally a directory can be
specified in which the images will be read from:

```bash
cd tests/helpers && python prepare_dataset_for_object_detection.py --directory [DIRECTORY PATH]
```

The preparation steps are the following:

1. First select the golf ball on the after image window (for comparison the before image is also shown)
2. Select the golf hole

The following actions are allowed:

- Left click: Selects a point on the image
- Right click: Removes the selected point on the image
- Space: Saves the selected point (or None if not selected) and goes to the next step
- q: Quits preparation and saves data that have been selected

After running the script, the expected values will be exported to test_data.json

# Deploy

In order to deploy the module for use on the production server, use the deployment script as follows:

```
python deploy.py
```

This script will create a minimized version of the ace-distance module ready for deployment on the production server,
and a zipped version of it. The minimized version includes only the necessary modules and packages to run the algorithm.

# Creating a new layout

To create a new layout, use the script 'create_new_layout.py' in the root folder. It will automatically create a new
folder in acedistance/layouts with the specified name (first argument) and all the corresponding subfolders and
necessary files.

Example usage:

```
python create_new_layout.py "demo" --description="Grid layout for cameras in Amsterdam" --node_distance=2 --grid_imgs_path=path/to/imgs/dir
```

The first positional argument is the name of the layout which is required in every case. The following parameters are
optional that are described here:

- --description: Short description of the new layout.
- --node_distance: Uniform distance between nodes in meters (default is 2 meters).
- --grid_imgs_path: Path to the folder containing the images of the grid layout that are used to define the grid node
  positions.

After creating a new layout, the grid.json file has to be fine-tuned for the new camera which requires additional steps:

- Specify node positions
- Specify border of green field

These steps can be done separately using the following scripts:

- Specify node positions:
  ```
  python acedistance/helpers/grid/set_grid_points_col_wise.py
  ```

- Specify border of green field:
  ```
  python create_new_mask.py [layout_name]
  ```
  The script loads the first image it finds under acedistance/layouts/[layout_name]/imgs therefore the layout images
  that define the grid node positions should had been copied to this folder before running this script.

After using the described helper functions, the obtained data have to be copied to the grid.json file to the correct
property.

# Making a release

The release process for the ace-disance module is the following:

1. Checkout on a new release branch
2. Change VERSION and RELEASE_DATE values in config/config.ini
3. Run pytest and make sure all tests pass
4. Make a deployed version for the production server using deploy.py
5. Copy the deployed version in a different folder, run the setup script and test it manually with a few images
6. Push changes to repository, create a new tag and merge branch into main
7. Copy the deployed version to the production server and replace the previous version with it
8. Optionally test the deployed version on the server in docker environment and/or ask Bram to run a full system test in
   order to make sure everything is working correctly