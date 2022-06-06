import os
import cv2
import numpy as np
from shapely.geometry.polygon import Polygon


class ObjectDetection:
    def __init__(self, img_before_path, img_after_path, gridlayout, out_dir, debug_mode=False):
        self.gridlayout = gridlayout

        # Load before/after images
        self.img_before_path = img_before_path
        if not os.path.isfile(self.img_before_path):
            raise FileNotFoundError(f'Image (before) not found on path: {self.img_before_path}')
        self.img_before = cv2.imread(self.img_before_path)

        self.img_after_path = img_after_path
        if not os.path.isfile(self.img_after_path):
            raise FileNotFoundError(f'Image (after) not found on path: {self.img_after_path}')
        self.img_after = cv2.imread(self.img_after_path)

        self.out_dir = out_dir
        self.debug_mode = debug_mode

        if debug_mode:
            # Create folder for debug images
            self.out_dir_hole = f"{self.out_dir}/hole"
            if not os.path.exists(self.out_dir_hole):
                os.makedirs(self.out_dir_hole)

            self.out_dir_ball = f'{self.out_dir}/ball'
            if not os.path.exists(self.out_dir_ball):
                os.makedirs(self.out_dir_ball)

    def isContourCrossingField(self, contour):
        """
        Checks whether the given contour intersects the green field in a way that it has points
        within and also outside the green field.

        (Shapely does this by checking if the dimension of the intersection is less than the dimension of the one
        or the other shapes.)
        """

        if contour.shape[0] < 3:
            # If contour doesn't have enough points to make a Polygon, return False
            return False

        field_border_points = self.gridlayout.layout['mask']['field_border']
        valid_area = Polygon(field_border_points)

        contour = np.squeeze(contour)
        polygon = Polygon(contour)

        return polygon.intersects(valid_area)

    def isContourInFieldStrict(self, contour):
        """
        Returns whether the contour is contained inside the green field (strict). As opposed to isContourInField, this method
        does a strict check meaning the contour has to be fully contained (cannot intersect its borders) to return true.
        It is used for ball detection as the ball has to be fully contained within the green field's area.
        """

        if contour.shape[0] < 3:
            # If contour doesn't have enough points to make a Polygon, return False
            return False

        field_border_points = self.gridlayout.layout['mask']['field_border']
        valid_area = Polygon(field_border_points)

        contour = np.squeeze(contour)
        polygon = Polygon(contour)

        return valid_area.covers(polygon)

    def isContourInFieldWeak(self, contour):
        """
        Returns whether the contour is contained inside the green field (weak). As opposed to isContourInFieldStrict, this method
        does a weak check meaning the contour can intersect and reach out of the green fields borders to return true.
        It is used for hole detection as the top of the flag can often go out of the green field's area.
        """

        return self.isContourInFieldStrict(contour) or self.isContourCrossingField(contour)

    def sizeRestrictionHole(self, contour):
        if not 100 < cv2.contourArea(contour) < 1000:
            return False

        return True

    def sizeRestrictionBall(self, contour):
        if not 2 < cv2.contourArea(contour) < 50:
            return False

        return True

    def dimensionRestrictionBall(self, contour):
        x, y, w, h = cv2.boundingRect(contour)
        if not (w < 25 and h < 25):
            return False

        return True

    def apply(self, img, cnts, r_functions):
        """
        Applies an array of restriction functions on the detected contours and discards the ones on the image
        that do not pass all the functions.

        :param img: Image where the contours where detected on
        :param cnts: Array of CV2 Contours
        :param r_functions: Array of restriction functions that should be checked on each contour
        :return: Return array of contours that passed each restriction functions
        """

        for c in cnts:
            if not np.array([f(c) for f in r_functions]).all():
                cv2.drawContours(img, [c], 0, (0, 0, 0), -1)

        return img

    def findAceHole(self):
        # Apply opencv masks for hole detection
        img = self.img_after.copy()
        w, h = self.gridlayout.layout['mask']['img_dimensions']

        # Apply grayscale
        cv_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/1gray.jpg", cv_gray)

        # Apply erode to strength contours
        element = np.ones((5, 5))
        cv_erode = cv2.erode(cv_gray, element)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/2erode.jpg", cv_erode)

        # Threshold detection
        cv_thresh = cv2.adaptiveThreshold(cv_erode, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 37, 10)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/3tresh.jpg", cv_thresh)

        # Remove small noise from image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))
        cv_opening = cv2.morphologyEx(cv_thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/4morph.jpg", cv_opening)

        # Apply dilate to connect broken white contours
        element = np.ones((4, 2))
        cv_dilate = cv2.dilate(cv_opening, element)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/5dilate.jpg", cv_dilate)

        cnts, _ = cv2.findContours(cv_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        img = self.apply(
            img=cv_dilate,
            cnts=cnts,
            r_functions=[
                self.isContourInFieldWeak,
                self.sizeRestrictionHole
            ])

        if self.debug_mode:
            cv2.imwrite(f"{self.out_dir_hole}/6apply.jpg", img)

        cnts, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Select final contour
        selected_contour = None
        max_area = 0

        for c in cnts:
            c = np.squeeze(c)
            area = cv2.contourArea(c)

            x_min = np.min(c[:, 0])
            x_max = np.max(c[:, 0])
            x_avg = np.mean(c[:, 0])

            y_min = np.min(c[:, 1])
            y_max = np.max(c[:, 1])

            # Too close to edge of the image, it cannot be the hole
            height_width_ratio = (y_max - y_min) / (x_max - x_min)
            if height_width_ratio < 2:
                if area > max_area:
                    continue

            if area > max_area:
                selected_contour = c
                max_area = area

        if selected_contour is None:
            return None

        y = max(selected_contour[:, 1])
        x = int(np.mean(np.array([v for v in selected_contour if v[1] == y])[:, 0]))

        # Draw the contour on the new mask and perform the bitwise operation
        pos_ace_hole = (x, y - 5)
        img_result = cv2.circle(self.img_after.copy(), pos_ace_hole, 2, (0, 0, 255), 2)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/7result.jpg", img_result)

        return pos_ace_hole

    def findGolfBall(self):
        img_before = self.img_before.copy()
        img_after = self.img_after.copy()

        # Get contours and subtract the contours from the before image
        contours_before = self.getContoursForBall(img_before)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/2a_contours_before.jpg", contours_before)

        # Enlarge found contours on before image for subtraction
        element = np.ones((4, 4))
        contours_before_dilate = cv2.dilate(contours_before, element)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3a_contours_before_dilate.jpg", contours_before_dilate)

        contours_after = self.getContoursForBall(img_after)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/2b_contours_after.jpg", contours_after)

        # Enlarge found contours on after image for subtraction (not as much as on the before image)
        element = np.ones((3, 2))
        contours_after_dilate = cv2.dilate(contours_after, element)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3b_contours_after_dilate.jpg", contours_after_dilate)

        contours = cv2.subtract(contours_after_dilate, contours_before_dilate)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/4contours_substract.jpg", contours)

        # Apply morphology for cleaning up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cv_opening = cv2.morphologyEx(contours, cv2.MORPH_OPEN, kernel, iterations=1)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/5morph.jpg", cv_opening)

        cnts, _ = cv2.findContours(cv_opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        img = self.apply(
            img=cv_opening,
            cnts=cnts,
            r_functions=[
                self.isContourInFieldStrict,
                self.sizeRestrictionBall,
                self.dimensionRestrictionBall
            ])

        if self.debug_mode:
            cv2.imwrite(f"{self.out_dir_ball}/6apply.jpg", img)

        cnts, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # --------------------------------------------------------------------
        # brief: The algorithm chooses the contour with the largest area(=radius * math.pi)

        selected_contour = None
        max_radius = 0

        for c in cnts:
            c = np.squeeze(c)
            _, radius = cv2.minEnclosingCircle(c)

            if radius > max_radius:
                selected_contour = c
                max_radius = radius

        # --------------------------------------------------------------------

        # Create a new mask for the result image
        if selected_contour is not None:
            x = int(np.ceil(np.mean(selected_contour[:, 0])))
            y = int(np.ceil(np.mean(selected_contour[:, 1])))

            # Draw the contour on the new mask and perform the bitwise operation
            # res = cv2.drawContours(image, [cnt2],-1, 255, -1)
            pos_ball = (x, y)
            img_result = cv2.circle(img_after, pos_ball, 2, (0, 0, 255), 2)

            if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/7result.jpg", img_result)

            return pos_ball

        return None

    def getContoursForBall(self, img):
        cv_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv_gray = cv2.bitwise_not(cv_gray)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/1gray.jpg", cv_gray)

        cv_thresh = cv2.adaptiveThreshold(cv_gray, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 60)

        return cv_thresh
