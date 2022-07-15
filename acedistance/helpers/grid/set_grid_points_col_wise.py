import os
import cv2
import json
import argparse
from linear_regression import linear_regression

grid_points = {
    "nodes": []
}

prevPoints = (0, 0)
row = []


def click_event(event, x, y, flags, params):
    global grid_points, row, prevPoints

    # Check for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        if y < prevPoints[1]:
            '''
            X = [node[0] for node in row if node != []]
            Y = [node[1] for node in row if node != []]

            regression_data = linear_regression(X, Y)

            # Fill out the missing nodes with empty ones
            if len(regression_data) != 9:
                regression_data.insert(0, [])

            for i in range(0, 9 - len(regression_data)):
                regression_data.append([])

            grid_points["nodes"].append(regression_data)
            grid_points["nodes"].append(row)
            '''
            # Fill out the missing nodes with empty ones
            if len(row) != 9:
                row.insert(0, [])

            for i in range(0, 9 - len(row)):
                row.append([])
            print(row)
            grid_points["nodes"].append(row)
            row = []
        else:
            row.append((x, y))

        prevPoints = (x, y)

        # Draw a circle of red color of thickness -1 px
        cv2.circle(img, (x, y), 3, (0, 0, 255), 1)
        cv2.imshow('image', img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Flags: --layout LAYOUT
    parser.add_argument("-layout", "--layout", help="Which layout to choose")
    parser.add_argument("-image", "--image", help="Which image to choose")
    args = parser.parse_args()

    if not args.layout:
        exit("--layout flag not specified!")

    # Read and display specified image
    img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'layouts', args.layout, 'imgs', args.image)
    img = cv2.imread(img_path)
    cv2.imshow('image', img)

    # Load grid config
    if not os.path.isfile('node_points.json'):
        node_points = {
            'nodes': []
        }

        with open('node_points.json', 'w') as f:
            json.dump(node_points, f)

    with open('node_points.json', 'r') as f:
        g_json = json.load(f)
        grid_points['nodes'] = g_json['nodes']

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('image', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Print and save grid points in 'out_dir' before closing window
    print(grid_points)
    with open('node_points.json', 'w') as f:
        json.dump(grid_points, f)

    # Close window
    cv2.destroyAllWindows()
