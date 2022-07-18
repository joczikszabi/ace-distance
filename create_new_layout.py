import os
import json
import argparse
from distutils.dir_util import copy_tree


def create_layout(layout_name, description=None, node_distance=2, grid_imgs_path=None):
    """
    Creates a new layout under acedistance/layouts. This function only creates the necessary files and folders but
    the layout definition file (grid.json) will have to be set up separately.

    Args:
        layout_name (str): Name of the new layout
        description (str): Short description of the new layout
        node_distance (int): Uniform distance between nodes in meters (default is 2 meters)
        grid_imgs_path (str): Path to the images of the grid layout that are used to define the grid node positions

    Returns:
        Creates necessary folders / files for a new grid layout under acedistance/layouts with the specified name
    """

    LAYOUTS_DIR = os.path.join('acedistance', 'layouts')
    NEW_LAYOUT_DIR = os.path.join(LAYOUTS_DIR, layout_name)
    IMGS_DIR = os.path.join(NEW_LAYOUT_DIR, 'imgs')
    GRID_FILE = os.path.join(NEW_LAYOUT_DIR, 'grid.json')

    if os.path.isdir(NEW_LAYOUT_DIR):
        raise ValueError(f'Layout already exists with name \'{layout_name}\'')

    # Create necessary folders
    os.makedirs(NEW_LAYOUT_DIR)
    os.makedirs(IMGS_DIR)

    # Copy grid images to the 'imgs' folder if path is given
    if grid_imgs_path:
        if not os.path.isdir(grid_imgs_path):
            raise ValueError(f'Grid images path does not exist: {grid_imgs_path}')

        copy_tree(grid_imgs_path, IMGS_DIR)

    # Create template definition file
    grid_definition = {
        'name': layout_name,
        'description': description,
        'mask': {
            'img_dimensions': [1920, 1080],
            'field_border': None
        },
        'distance_between_nodes': node_distance,
        'nodes': None
    }
    with open(GRID_FILE, 'w') as f:
        json.dump(grid_definition, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a new layout definition')
    parser.add_argument('name',
                        type=str,
                        help='Name of the new layout.')

    parser.add_argument('-d',
                        '--description',
                        type=str,
                        help='Short description of the new layout.',
                        default=None,
                        required=False)

    parser.add_argument('-dist',
                        '--node_distance',
                        type=int,
                        help='Uniform distance between nodes in meters (default is 2 meters).',
                        default=2,
                        required=False)

    parser.add_argument('-g',
                        '--grid_imgs_path',
                        type=str,
                        help='Path to the images of the grid layout that are used to define the grid node positions.',
                        default=None,
                        required=False)

    args = parser.parse_args()

    try:
        # Run algorithm
        create_layout(
            layout_name=args.name,
            description=args.description,
            node_distance=args.node_distance,
            grid_imgs_path=args.grid_imgs_path
        )

    except Exception as e:
        print(f'Creating new layout failed: {e.args[0]}')
