import cv2

from helpers.utilities import plot_grid


def click_event(event, x, y, flags, params):
    global hole_coordinates

    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:

        if not hole_coordinates:
            hole_coordinates = (x, y)
            cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            cv2.imshow('image', img)

        else:
            # displaying the coordinates on the shell and image
            dist = round(estimator.estimateDistance((x, y), hole_coordinates, img), 2)

            print(f"Golf ball located at pixel coordinates: ({x}, {y})")
            print(f"Estimated distance between ball and hole: {dist} meter(s)\n")

            # displaying the coordinates on the image window
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.circle(img, (x, y), 2, (0, 255, 255), -1)
            cv2.putText(img, str(dist), (x, y), font, 1, (255, 0, 0), 2)
            cv2.imshow('image', img)


if __name__ == "__main__":
    # Load distance estimator object
    estimator = DistanceEstimation()
    hole_coordinates = ()

    # Read image
    #img_path = "./test_data/object_detection_test/layout2/test7-after.png"
    img_path = "../acedistance/layouts/layout2/imgs/01.png"
    img = cv2.imread(img_path, 1)

    # Display image and grid layout
    img = plot_grid(img, estimator.grid)
    cv2.imshow('image', img)

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('image', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Close window
    cv2.destroyAllWindows()
