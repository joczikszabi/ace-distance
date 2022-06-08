import cv2
import numpy as np
from shapely.geos import TopologicalError
from shapely.geometry.polygon import Polygon


def crossesFieldConstraint(contour, field_border_points, **_):
    """ CONSTRAINT FUNCTION
    A constraint function that checks whether the given contour intersects the green field in a way that
    it has points within and also outside the green field.

    Args:
        contour (np.array): List of points defining a contour returned from cv2
        field_border_points (np.array): List of points defining the valid area where detection should happen

    Returns:
        Bool: Returns True if contour intersects the green area, False otherwise
    """

    if contour.shape[0] < 3:
        # If contour doesn't have enough points to make a Polygon, return False
        return False

    valid_area = Polygon(field_border_points)

    contour = np.squeeze(contour)
    polygon = Polygon(contour)

    try:
        return polygon.intersects(valid_area)

    except TopologicalError:
        # Likely cause is invalidity of the geometry
        return False


def strictlyWithinFieldConstraint(contour, field_border_points, **_):
    """ CONSTRAINT FUNCTION
    A constraint function that checks whether the contour is contained inside the green field (strict).
    As opposed to withinFieldConstraint(), this method does a strict check meaning the contour has to be
    fully contained (cannot intersect its borders) to return true.

    It is used for ball detection as the ball has to be fully contained within the green field's area.

    Args:
        contour (np.array): List of points defining a contour returned from cv2
        field_border_points (np.array): List of points defining the valid area where detection should happen

    Returns:
        Bool: Returns True if contour is strictly within the green area, False otherwise.
    """

    if contour.shape[0] < 3:
        # If contour doesn't have enough points to make a Polygon, return False
        return False

    valid_area = Polygon(field_border_points)

    contour = np.squeeze(contour)
    polygon = Polygon(contour)

    try:
        return valid_area.covers(polygon)
    except TopologicalError:
        # Likely cause is invalidity of the geometry
        return False


def withinFieldConstraint(contour, field_border_points, **_):
    """ CONSTRAINT FUNCTION
    A constraint function that checks whether the contour is contained inside the green field (weak).
    As opposed to strictlyWithinFieldConstraint(), this method does a weak check meaning the contour can intersect and
    reach out of the green fields borders to return true.

    It is used for hole detection as the top of the flag can often go out of the green field's area.

    Args:
        contour (np.array): List of points defining a contour returned from cv2
        field_border_points (np.array): List of points defining the valid area where detection should happen

    Returns:
        Bool: Returns True if contour is within the green area or intersects it, False otherwise.
    """

    return strictlyWithinFieldConstraint(contour, field_border_points) or crossesFieldConstraint(contour,
                                                                                                 field_border_points)


def areaConstraint(contour, min_area=2, max_area=1000, **_):
    """ CONSTRAINT FUNCTION
    A constraint function that checks for the area size of the contour.

    Args:
        contour (np.array): List of points defining a contour returned from cv2
        min_area (Int): The minimum accepted area of a contour
        max_area (Int): The maximum accepted area of a contour

    Returns:
        Bool: Returns True if the size of the contour's area is within the acceptable range, False otherwise.
    """

    if not min_area < cv2.contourArea(contour) < max_area:
        return False

    return True


def dimensionConstraint(contour, min_width=1, max_width=50, min_height=2, max_height=250, **_):
    """ CONSTRAINT FUNCTION
    A constraint function that checks for the dimension of the contour.

    Args:
        contour (np.array): List of points defining a contour returned from cv2
        min_width (Int): The minimum accepted width of a contour
        max_width (Int): The maximum accepted width of a contour
        min_height (Int): The minimum accepted width of a contour
        max_height (Int): The maximum accepted width of a contour

    Returns:
        Bool: Returns True if the dimension of the contour is within the acceptable range, False otherwise.
    """

    x, y, w, h = cv2.boundingRect(contour)
    if not (min_width < w < max_width and min_height < h < max_height):
        return False

    return True


def heightWidthRatioConstraint(contour, min_height_width_ratio=2, max_height_width_ratio=10, **_):
    """ CONSTRAINT FUNCTION
    A constraint function that checks for the height / width ratio of the object.

    Args:
        contour (np.array): List of points defining a contour returned from cv2
        min_height_width_ratio: The minimum accepted height/width ratio of a contour
        max_height_width_ratio: The maximum accepted height/width ratio of a contour

    Returns:
        Bool: Returns True if the height / width ratio of the contour is within the acceptable range, False otherwise.
    """

    x, y, w, h = cv2.boundingRect(contour)
    height_width_ratio = h / w

    if not (min_height_width_ratio < height_width_ratio < max_height_width_ratio):
        return False

    return True
