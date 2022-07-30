import os
import cv2
import glob
import numpy as np
from shapely.geometry.polygon import Polygon


def draw_mask(img_path, mask_points):
    """ Helps rendering the mask points on the given image using opencv.

    Args:
        img_path (str): Path to the image on which the mask points should be rendered
        mask_points (list(list(list(int))): List of mask points defining the field border

    Returns:
        None
    """

    img = cv2.imread(img_path)
    overlay = img.copy()
    int_coords = lambda x: np.array(x).round().astype(np.int32)
    alpha = 0.15  # that's your transparency factor

    # Draw field
    field = Polygon(mask_points)
    exterior = [int_coords(field.exterior.coords)]
    cv2.fillPoly(overlay, exterior, color=(255, 255, 0))
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    cv2.imshow('Mask', img)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    return img


def set_mask_points(layout_name):
    """ Helps defining mask points for a given layout.

    The function opens the first image in acedistance/layouts/[layout_name]/imgs on which the users can select the points
    of the field border using left mouse click. After selecting the points, the points will be stored in a 2D list
    which can be embedded in the grid.json definition file.

    Args:
        layout_name (str): Name of the layout for which the mask will be created

    Returns:
        File: Exports border point coordinates to mask_point.json
    """

    # Read and display specified image
    IMGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'layouts', layout_name, 'imgs')

    try:
        img_path = glob.glob(os.path.join(IMGS_PATH, '*.png'), recursive=False)[0]  # take first image in folder
    except IndexError:
        exit(f'Could not find any images under {IMGS_PATH}. Make sure images have .png extension.')

    img = cv2.imread(os.path.join(IMGS_PATH, img_path))
    cv2.imshow('Select field border points', img)

    mask_points = []

    def click_event(event, x, y, flags, params):
        # Check for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            mask_points.append((x, y))

            # Draw a circle of red color of thickness -1 px
            cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
            cv2.imshow('Select field border points', img)

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('Select field border points', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Close window
    cv2.destroyAllWindows()

    return mask_points
