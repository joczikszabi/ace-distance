import os
import cv2
import glob
import json
import argparse
from acedistance.helpers.grid import draw_nodes, set_nodes


def create_nodes(layout_name, n_rows, n_cols):
    """
    Creates a list of grid node points for the given layout. The selected points will be exported in nodes.json

    Args:
        layout_name (str): Name of the layout for which the mask will be created
        n_rows (int): Maximum number of rows in the complete grid layout
        n_cols (int): Maximum number of columns in the complete grid layout

    Returns:
        File: Exports grid node points to nodes.json
    """

    LAYOUT_DIR = os.path.join('acedistance', 'layouts', layout_name)
    IMGS_PATH = os.path.join(LAYOUT_DIR, 'imgs')
    GRID_FILE = os.path.join(LAYOUT_DIR, 'grid.json')

    try:
        img_path = glob.glob(os.path.join(IMGS_PATH, '*.png'), recursive=False)[0]
    except IndexError:
        exit(f'Could not find any images under {IMGS_PATH}. Make sure images have .png extension.')

    if not os.path.isfile(GRID_FILE):
        raise ValueError(f'Layout does not exist \'{layout_name}\'')

    # Set node points
    nodes = set_nodes(img_path, n_rows, n_cols)

    # Draw nodes
    draw_nodes(img_path, nodes)
    cv2.destroyAllWindows()

    # Save node points before closing window
    with open('nodes.json', 'w') as f:
        json.dump(nodes, f)

    print(f'Node points have been successfully exported in nodes.json...')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a list of grid nodes for the given layout.')
    parser.add_argument('layout',
                        type=str,
                        help='Name of the layout file.')

    parser.add_argument('-r',
                        '--nrows',
                        type=int,
                        help='Maximum number of rows in the complete grid layout.',
                        required=True)

    parser.add_argument('-c',
                        '--ncols',
                        type=int,
                        help='Maximum number of columns in the complete grid layout.',
                        required=True)

    args = parser.parse_args()

    try:
        create_nodes(layout_name=args.layout, n_rows=args.nrows, n_cols=args.ncols)

    except Exception as e:
        print(f'Creating new nodes failed: {e.args[0]}')
