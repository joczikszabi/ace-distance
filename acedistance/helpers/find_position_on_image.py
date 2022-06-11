"""
Returns the location (in pixels) of a select a point on the specified image
"""

import cv2
import argparse
from acedistance.helpers.load import loadConfig


def find_position_on_image(img_before_path, img_after_path):
    pos_ball = find_ball_position_on_image(img_before_path, img_after_path)
    if pos_ball is None:
        return None

    pos_hole = find_hole_position_on_image(img_after_path)
    if pos_hole is None:
        return None

    return {
        "pos_ball": pos_ball,
        "pos_hole": pos_hole
    }


def find_ball_position_on_image(img_before_path, img_after_path):
    img_b = cv2.imread(img_before_path, 1)
    img_a = cv2.imread(img_after_path, 1)
    position = []

    def click_event(event, x, y, flags, params):
        nonlocal position  # access outer 'position' variable

        if event == cv2.EVENT_LBUTTONDOWN:
            # Re-render image and delete any previous circles rendered on it
            img_a_tmp = img_a.copy()
            cv2.imshow('(Image before)', img_b.copy())
            cv2.imshow('Select ball (Image after)', img_a_tmp)

            # Save selected pixels
            position = [x, y]
            cv2.circle(img_a_tmp, tuple(position), 5, (0, 0, 255), -1)
            cv2.imshow('Select ball (Image after)', img_a_tmp)

        elif event == cv2.EVENT_RBUTTONDOWN:
            # Remove position
            position = []
            img_a_tmp = img_a.copy()
            cv2.imshow('Select ball (Image after)', img_a_tmp)

    cv2.imshow('(Image before)', img_b.copy())
    cv2.imshow('Select ball (Image after)', img_a.copy())
    cv2.setMouseCallback('Select ball (Image after)', click_event)
    key = cv2.waitKey(0)

    if key == ord('q'):
        return None

    print(f"Ball is located at: {position}")
    cv2.destroyAllWindows()

    return position


def find_hole_position_on_image(img_after_path):
    img_a = cv2.imread(img_after_path, 1)
    position = []

    def click_event(event, x, y, flags, params):
        nonlocal position  # access outer 'position' variable

        if event == cv2.EVENT_LBUTTONDOWN:
            # Re-render image and delete any previous circles rendered on it
            img_a_tmp = img_a.copy()
            cv2.imshow('Select hole', img_a_tmp)

            # Save selected pixels
            position = [x, y]
            cv2.circle(img_a_tmp, tuple(position), 5, (0, 0, 255), -1)
            cv2.imshow('Select hole', img_a_tmp)

    cv2.imshow('Select hole', img_a.copy())
    cv2.setMouseCallback('Select hole', click_event)
    key = cv2.waitKey(0)

    if key == ord('q'):
        return None

    print(f"Hole is located at: {position}")
    cv2.destroyAllWindows()

    return position


if __name__ == "__main__":
    configParser = loadConfig()
    layout_name = configParser['GRID']['LAYOUT_NAME']

    parser = argparse.ArgumentParser(description='This function returns the position of a selected point on an image.')
    parser.add_argument('img_before_path',
                        type=str,
                        help='Path to the after image.')
    parser.add_argument('img_after_path',
                        type=str,
                        help='Path to the before image.')
    args = parser.parse_args()

    find_position_on_image(args.img_before_path, args.img_after_path)
