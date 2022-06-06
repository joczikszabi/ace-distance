import cv2
import numpy as np


def draw_mask(image, field, contour):
    overlay = image.copy()
    int_coords = lambda x: np.array(x).round().astype(np.int32)
    alpha = 0.5  # that's your transparency factor

    # Draw field
    exterior = [int_coords(field.exterior.coords)]
    cv2.fillPoly(overlay, exterior, color=(255, 255, 0))
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    # Draw contour
    exterior = [int_coords(contour.exterior.coords)]
    cv2.fillPoly(overlay, exterior, color=(0, 0, 255))
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    return image
