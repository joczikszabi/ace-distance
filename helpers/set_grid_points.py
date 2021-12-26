import os
import sys
import cv2
import json
import argparse

grid_points = {
    "nodes": []
}

prevPoints = (0, 0)
row = []

def click_event(event, x, y, flags, params):
    global grid_points, row, prevPoints

    # Check for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        if (x < prevPoints[0]):
            grid_points["nodes"].append(row)
            print(row)
            row = []
            row.append((x,y))
        else:
            row.append((x,y))

        prevPoints = (x,y)

        # Draw a circle of red color of thickness -1 px
        cv2.circle(img, (x,y), 3, (0, 0, 255), 1)
        cv2.imshow('image', img)

if __name__=="__main__":

    parser = argparse.ArgumentParser()

    #Flags: --layout LAYOUT
    parser.add_argument("-layout", "--layout", help="Which part of the layout")
    args = parser.parse_args()

    if not args.layout:
        exit("--layout flag not specified!")
 
    # Read and display specified image
    img = cv2.imread(f'../references/layout_{args.layout}.jpg', 1)
    cv2.imshow('image', img)
 
    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('image', click_event)
 
    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Create directory for outputs
    out_dir = "./tmp"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Print and save grid points in 'out_dir' before closing window
    print(grid_points)
    with open(f"{out_dir}/grid.json", "w") as f:
        json.dump(grid_points, f)
 
    # Close window
    cv2.destroyAllWindows()