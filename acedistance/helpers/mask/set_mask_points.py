import os
import cv2
import json
import argparse


def set_mask_points(layout):

    # Read and display specified image
    IMGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'layouts', layout, 'imgs')
    img_name = os.listdir(IMGS_PATH)[0]  # take first image in folder
    img = cv2.imread(os.path.join(IMGS_PATH, img_name))
    cv2.imshow('image', img)

    mask_points = []

    def click_event(event, x, y, flags, params):
        # Check for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            mask_points.append((x, y))

            # Draw a circle of red color of thickness -1 px
            cv2.circle(img, (x, y), 3, (0, 0, 255), 1)
            cv2.imshow('image', img)

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('image', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Close window
    cv2.destroyAllWindows()

    return mask_points


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Flags: --layout LAYOUT
    parser.add_argument("-layout",
                        "--layout",
                        help="Which layout to choose",
                        required=True)
    args = parser.parse_args()

    mask_points = set_mask_points(args.layout)

    # Print and save mask points before closing window
    print(mask_points)
    with open('mask_point.json', 'w') as f:
        json.dump(mask_points, f)
