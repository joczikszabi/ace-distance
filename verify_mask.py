import os
import glob
import argparse
from acedistance.helpers.mask import draw_mask
from acedistance.helpers.load import loadLayout


def verify_mask(layout_name):
    """
    Renders the given layout's corresponding mask which represents its valid field border.

    Args:
        layout_name (str): Name of the layout for which the mask will be created

    Returns:
        None
    """

    LAYOUT_DIR = os.path.join('acedistance', 'layouts', layout_name)
    IMGS_PATH = os.path.join(LAYOUT_DIR, 'imgs')
    GRID_FILE = os.path.join(LAYOUT_DIR, 'grid.json')

    if not os.path.isfile(GRID_FILE):
        raise ValueError(f'Layout does not exist \'{layout_name}\'')

    # Set mask points
    layout = loadLayout(layout_name)
    mask_points = layout['mask']['field_border']

    # Draw mask
    try:
        img_path = glob.glob(os.path.join(IMGS_PATH, '*.png'), recursive=False)[0]
    except IndexError:
        exit(f'Could not find any images under {IMGS_PATH}. Make sure images have .png extension.')

    draw_mask(img_path, mask_points)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Renders a given layout\'s mask representing its field border.')
    parser.add_argument('layout',
                        type=str,
                        help='Name of the layout file.')

    args = parser.parse_args()

    try:
        # Run algorithm
        verify_mask(layout_name=args.layout)

    except Exception as e:
        print(f'Rendering mask failed: {e.args[0]}')
