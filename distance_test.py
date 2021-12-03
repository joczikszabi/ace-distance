import sys
import cv2
import numpy as np

from main.DistanceEstimation import DistanceEstimation
from helpers.plot_grid import plot_grid

def click_event(event, x, y, flags, params):
    global hole_coordinates

    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:

        if not hole_coordinates:
            hole_coordinates = (x,y)

            font = cv2.FONT_HERSHEY_SIMPLEX
            #cv2.putText(img, str(x) + ',' + str(y), (x,y), font, 1, (255, 0, 0), 2)
            cv2.putText(img, "Hole", (x,y), font, 1, (255, 0, 0), 2)
            cv2.imshow('image', img)

        else:
            # displaying the coordinates on the shell and image
            res = estimator.estimateDistance((x,y), hole_coordinates)
            d = round(res[0], 2)
            print(res)
            print(f"Golf ball located at pixel coordinates: ({x}, {y})")
            print(f"Estimated distance between ball and hole: {d} meter(s)\n")

            # displaying the coordinates
            # on the image window
            font = cv2.FONT_HERSHEY_SIMPLEX
            #cv2.putText(img, str(x) + ',' + str(y), (x,y), font, 1, (255, 0, 0), 2)
            cv2.circle(img, (int(res[1][0][0]), int(res[1][0][1])), 3, (0, 0, 255), 1)
            cv2.circle(img, (int(res[1][1][0]), int(res[1][1][1])), 3, (0, 0, 255), 1)
            cv2.putText(img, str(d), (x,y), font, 1, (255, 0, 0), 2)
            cv2.imshow('image', img)

if __name__=="__main__":

    estimator = DistanceEstimation()
    hole_coordinates = ()

    # reading the image
    img = cv2.imread('./reference.png', 1)
 
    # displaying the image
    cv2.imshow('image', img)

    plot_grid(img, estimator.grid)
 
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback('image', click_event)
 
    # wait for a key to be pressed to exit
    cv2.waitKey(0)
 
    # close the window
    cv2.destroyAllWindows()