import os
import sys
import cv2

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from acedistance.helpers.load import loadConfig
from acedistance.main.Grid import GridLayout
from acedistance.helpers.grid import draw_nodes
from acedistance.main.DistanceEstimation import DistanceEstimation


def click_event(event, x, y, flags, params):
    global hole_coordinates

    # Checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:

        if not hole_coordinates:
            hole_coordinates = (x, y)
            cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            cv2.imshow('Distance estimation', img)

        else:
            # displaying the coordinates on the shell and image
            dist = round(estimator.estimateDistance((x, y), hole_coordinates), 2)

            print(f"Golf ball located at pixel coordinates: ({x}, {y})")
            print(f"Estimated distance between ball and hole: {dist} meter(s)\n")

            # displaying the coordinates on the image window
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.circle(img, (x, y), 2, (0, 255, 255), -1)
            cv2.putText(img, str(dist), (x, y), font, 1, (255, 0, 0), 2)
            cv2.imshow('Distance estimation', img)


if __name__ == "__main__":
    configParser = loadConfig()
    layout_name = configParser['GRID']['LAYOUT_NAME']
    gridlayout = GridLayout(layout_name)

    # Load distance estimator object
    estimator = DistanceEstimation(gridlayout)
    hole_coordinates = ()

    # Read image
    # img_path = "./test_data/object_detection_test/layout2/test7-after.png"
    # img_path = "../acedistance/layouts/f4db010a-5dba-4708-b758-24aaad97a48e/imgs/01.png"
    img_path = "test_data/object_detection_test/fa8bd53e-e028-48ae-8419-bd5ea6909ceb-after.png"

    # Display image and grid layout
    img = draw_nodes(img_path, gridlayout.getGridNodes(), indices_on=False, auto_open=False)
    cv2.destroyAllWindows()
    cv2.imshow('Distance estimation', img)

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('Distance estimation', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Close window
    cv2.destroyAllWindows()
