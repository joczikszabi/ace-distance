import cv2
import numpy as np
from shapely.geometry.polygon import Polygon


def draw_mask(image_path, mask_points):
    image = cv2.imread(image_path)
    overlay = image.copy()
    int_coords = lambda x: np.array(x).round().astype(np.int32)
    alpha = 0.5  # that's your transparency factor

    # Draw field
    field = Polygon(mask_points)
    exterior = [int_coords(field.exterior.coords)]
    cv2.fillPoly(overlay, exterior, color=(255, 255, 0))
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    cv2.imshow('mask', image)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)


if __name__ == "__main__":
    pass
