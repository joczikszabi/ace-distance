import os
import cv2
import glob
import json
import argparse
from acedistance.helpers.mask import draw_mask, set_mask_points


def create_mask(layout_name):
    """
    Creates a new mask for a layout. The selected points will be exported in mask_points.json

    Args:
        layout_name (str): Name of the layout for which the mask will be created

    Returns:
        File: Exports border point coordinates to mask_point.json
    """

    LAYOUT_DIR = os.path.join('acedistance', 'layouts', layout_name)
    IMGS_PATH = os.path.join(LAYOUT_DIR, 'imgs')
    GRID_FILE = os.path.join(LAYOUT_DIR, 'grid.json')

    if not os.path.isfile(GRID_FILE):
        raise ValueError(f'Layout does not exist \'{layout_name}\'')

    # Set mask points
    mask_points = set_mask_points(layout_name)

    # Draw mask
    try:
        img_path = glob.glob(os.path.join(IMGS_PATH, '*.png'), recursive=False)[0]
    except IndexError:
        exit(f'Could not find any images under {IMGS_PATH}. Make sure images have .png extension.')

    draw_mask(img_path, mask_points)
    cv2.destroyAllWindows()

    # Save mask points before closing window
    with open('mask_point.json', 'w') as f:
        json.dump(mask_points, f)

    print(f'Mask points have been successfully exported in mask_points.json...')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a new mask for a layout.')
    parser.add_argument('layout',
                        type=str,
                        help='Name of the layout file.')

    args = parser.parse_args()

    try:
        # Run algorithm
        create_mask(layout_name=args.layout)

    except Exception as e:
        print(f'Creating new mask failed: {e.args[0]}')
