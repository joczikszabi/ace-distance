""" Makes it easy to prepare expected values for the images for object detection test on every image
found in the specified folder

If no folder is specified, by default the test_data/object_detection_test folder is used

Returns:
    expected_values.json (json): Json file containing the expected values of the processed images
"""

import os
import sys
import json
import argparse

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../..'))

from acedistance.helpers.load import loadConfig
from acedistance.helpers.find_position_on_image import find_position_on_image


def prepare_dataset_in_folder(directory):
    output = []

    for filename in os.listdir(directory):
        if filename.endswith('-after.png'):
            suffix = '-after.png'
            recording_id = filename[:-len(suffix)]

            img_path_before = os.path.join(directory, f'{recording_id}-before.png')
            img_path_after = os.path.join(directory, f'{recording_id}-after.png')

            positions = find_position_on_image(img_path_before, img_path_after)

            if positions is None:
                print('User exited image preparation...')
                break

            img_data = {
                "img_name": recording_id,
                "layout": layout_name,
                "hole_position": positions['pos_hole'],
                "ball_position": positions['pos_ball']
            }
            output.append(img_data)

    with open('../test_data/object_detection_test/test_data.json', 'w') as f:
        json.dump(output, f)


if __name__ == "__main__":
    configParser = loadConfig()
    layout_name = configParser['GRID']['LAYOUT_NAME']

    parser = argparse.ArgumentParser(
        description='Allows to set the position of objects on the images stored in the given test folder.')
    parser.add_argument('-d',
                        '--directory',
                        type=str,
                        help='Path of the folder of the images of interest .',
                        required=False)
    args = parser.parse_args()

    if args.directory:
        prepare_dataset_in_folder(args.directory)

    else:
        dir_path = os.path.join("..", "test_data", "object_detection_test")
        prepare_dataset_in_folder(dir_path)
