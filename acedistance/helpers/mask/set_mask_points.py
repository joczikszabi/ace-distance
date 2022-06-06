import cv2
import json
import argparse

mask_points = []


def click_event(event, x, y, flags, params):
    global mask_points

    # Check for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        mask_points.append((x, y))

        # Draw a circle of red color of thickness -1 px
        cv2.circle(img, (x, y), 3, (0, 0, 255), 1)
        cv2.imshow('image', img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Flags: --layout LAYOUT
    parser.add_argument("-layout",
                        "--layout",
                        help="Which layout to choose",
                        required=True)
    args = parser.parse_args()

    # Read and display specified image
    layout_path = f'../layouts/{args.layout}'
    #img = cv2.imread(f'{layout_path}/imgs/{args.image}.png')
    img = cv2.imread(f'img.png')
    cv2.imshow('image', img)

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('image', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Print and save mask points before closing window
    print(mask_points)
    with open('mask_point.json', 'w') as f:
        json.dump(mask_points, f)

    # Close window
    cv2.destroyAllWindows()
