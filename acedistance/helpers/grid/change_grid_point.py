import json

import cv2

grid_points = {
    "nodes": []
}

prevPoints = (0, 0)
row = []

def click_event(event, x, y, flags, params):
    global grid_points, row, prevPoints

    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        if (x < prevPoints[0]):
            grid_points["nodes"].append(row)
            print(row)
            row = []
        else:
            row.append((x,y))

        prevPoints = (x,y)

        # Draw a circle of red color of thickness -1 px
        cv2.circle(img, (x,y), 3, (0, 0, 255), 1)
        cv2.imshow('image', img)

if __name__=="__main__":
 
    # reading the image
    img = cv2.imread('../../../out/layouts/layout2/imgs/01.jpeg', 1)
 
    # displaying the image
    cv2.imshow('image', img)
 
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback('image', click_event)
 
    # wait for a key to be pressed to exit
    cv2.waitKey(0)

    with open("../tmp/grid_transposed.json", "w") as f:
        json.dump(grid_points, f)
 
    # close the window
    cv2.destroyAllWindows()