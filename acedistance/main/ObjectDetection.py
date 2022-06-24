import os
import cv2
import numpy as np
from acedistance.main.constrains import withinFieldConstraint, strictlyWithinFieldConstraint, areaConstraint, \
    dimensionConstraint, heightWidthRatioConstraint, closeToBorderConstraint


class ObjectDetection:
    def __init__(self, img_before_path, img_after_path, gridlayout, out_dir, debug_mode=False):
        self.img_before_path = img_before_path
        self.img_before = cv2.imread(self.img_before_path)
        self.img_after_path = img_after_path
        self.img_after = cv2.imread(self.img_after_path)
        self.gridlayout = gridlayout
        self.out_dir = out_dir
        self.debug_mode = debug_mode
        self.n_masks_applied = 0
        self.current_outdir = None

        # Create folder for debug images
        self.out_dir_hole = f"{self.out_dir}/hole"
        self.out_dir_ball = f'{self.out_dir}/ball'
        if self.debug_mode:
            if not os.path.exists(self.out_dir_hole):
                os.makedirs(self.out_dir_hole)

            if not os.path.exists(self.out_dir_ball):
                os.makedirs(self.out_dir_ball)

    def findAceHole(self):
        """
        Prepares the image and applies a range of masks in order to find the position of the golf hole.

        Args:

        Returns:
            Bool: The position of the hole, None if not found
        """

        self.n_masks_applied = 0
        img = self.img_after.copy()

        # Apply masks for object detection
        img = self.applyGrayscale(img, out_dir=self.out_dir_hole)
        img = self.applyErode(img, (5, 5), out_dir=self.out_dir_hole)
        img = self.applyAdaptiveThreshold(img, 37, 10, out_dir=self.out_dir_hole)
        img = self.applyMorphology(img, (1, 6), 2, out_dir=self.out_dir_hole)
        img = self.applyDilate(img, (4, 2), out_dir=self.out_dir_hole)

        # Add constrains
        img = self.constrain(
            img=img,
            c_functions=[
                withinFieldConstraint,
                areaConstraint,
                heightWidthRatioConstraint,
                closeToBorderConstraint
            ],
            params={
                "field_border_points": self.gridlayout.layout['mask']['field_border'],
                "min_area": 100,
                "max_area": 1000,
                "min_width": 10,
                "max_width": 150,
                "min_height": 100,
                "max_height": 800,
                'extr_func': self.getCoordinateHole,
                'min_distance_from_border': 6,
                "min_height_width_ratio": 2,
                "max_height_width_ratio": 15
            },
            out_dir=self.out_dir_hole)

        # Select largest contour on image
        largest_contours = self.findContourWithLargestArea(img, lambda c: cv2.contourArea(c), num=2)
        if len(largest_contours) == 0:
            return None

        if len(largest_contours) == 1:
            selected_contour = np.squeeze(largest_contours[0])

        else:
            # If the two detected contours are the same pole but the top and bottom part of it, select the lower one
            area_diff = abs(cv2.contourArea(largest_contours[0]) - cv2.contourArea(largest_contours[1]))
            horizontal_pos_diff = abs(max(largest_contours[0][1, :, 0]) - max(largest_contours[1][1, :, 0]))
            if area_diff < 275 and horizontal_pos_diff < 20:
                selected_contour = self.selectContourWithLowestPosition(largest_contours)
                selected_contour = np.squeeze(selected_contour)

            # Else select the larger one
            else:
                selected_contour = np.squeeze(largest_contours[0])

        # Calculate final position of object, render it on image and return
        img_after_copy = self.img_after.copy()
        pos_ace_hole = self.getCoordinateHole(selected_contour)
        img_result = cv2.circle(img_after_copy, pos_ace_hole, 2, (0, 0, 255), 2)

        if self.debug_mode:
            cv2.imwrite(f"{self.out_dir_hole}/{self.n_masks_applied}_result.jpg", img_result)

        return pos_ace_hole

    def findGolfBall(self):
        """
        Prepares the images and applies a range of masks in order to find the position of the golf ball.

        Args:

        Returns:
            Bool: The position of the ball, None if not found
        """

        self.n_masks_applied = 0

        # First make some copies
        img_before = self.img_before.copy()
        img_after = self.img_after.copy()

        # Prepare before image
        img_before = self.applyGrayscale(img_before, out_dir=self.out_dir_ball)
        img_before = self.applyBitwiseNot(img_before, out_dir=self.out_dir_ball)
        img_before = self.applyAdaptiveThreshold(img_before, 17, 29, out_dir=self.out_dir_ball)
        img_before = self.applyDilate(img_before, (5, 5), out_dir=self.out_dir_ball)

        # Prepare after image
        img_after = self.applyGrayscale(img_after, out_dir=self.out_dir_ball)
        img_after = self.applyBitwiseNot(img_after, out_dir=self.out_dir_ball)
        img_after = self.applyAdaptiveThreshold(img_after, 13, 42, out_dir=self.out_dir_ball)
        img_after = self.applyDilate(img_after, (1, 1), out_dir=self.out_dir_ball)

        img = self.applySubtract(img_before, img_after, out_dir=self.out_dir_ball)
        img = self.applyDilate(img, (2, 2), out_dir=self.out_dir_ball)

        # Apply constrains
        constraint_params = {
            "field_border_points": self.gridlayout.layout['mask']['field_border'],
            "min_area": 1,
            "max_area": 40,
            "min_width": 2,
            "max_width": 25,
            "min_height": 1,
            "max_height": 25,
            "min_height_width_ratio": 0.5,
            "max_height_width_ratio": 1.67
        }

        img = self.constrain(img=img,
                             c_functions=[
                                 strictlyWithinFieldConstraint,
                                 areaConstraint,
                                 dimensionConstraint,
                                 heightWidthRatioConstraint
                             ],
                             params=constraint_params,
                             out_dir=self.out_dir_ball)

        # Select largest contour on image
        selected_contour = self.findContourWithLargestArea(img, lambda c: cv2.minEnclosingCircle(c)[1])
        selected_contour = np.squeeze(selected_contour)

        if len(selected_contour) == 0:
            return None

        # Calculate final position of object, render it on image and return
        img_after_copy = self.img_after.copy()
        pos_ball = self.getCoordinateBall(selected_contour)
        img_result = cv2.circle(img_after_copy, pos_ball, 2, (0, 0, 255), 2)

        if self.debug_mode:
            cv2.imwrite(f"{self.out_dir_ball}/{self.n_masks_applied}_result.jpg", img_result)

        return pos_ball

    def constrain(self, img, c_functions, params, out_dir):
        """
        Applies an array of constraint functions on the detected contours and discards the ones on the image
        that do not pass all the functions.

        Args:
            img (np.array): List of points defining contours returned from cv2
            c_functions ([functions]): Array of constraint functions that should be checked for each contour
            params (dict): Dictionary of parameters for the constraint functions (the necessary parameters are unpacked)
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns image where those contours that did not pass all restrictions are removed
        """

        cnts, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            if not np.array([f(c, **params) for f in c_functions]).all():
                cv2.drawContours(img, [c], 0, (0, 0, 0), -1)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_constrains.jpg", img)
            self.n_masks_applied += 1

        return img

    def getCoordinateHole(self, contour):
        """
        Calculates the (x,y) coordinates from a given contour for the golf hole.

        Args:
        contour ([np.array]): contour from where the coordinate needs to be extracted

        Returns:
        tuple: Returns (x, y) coordinate of the hole
        """

        y = max(contour[:, 1])
        x = int(np.mean(np.array([v for v in contour if v[1] == y])[:, 0]))

        return x - 1, y - 7

    def getCoordinateBall(self, contour):
        """
        Calculates the (x,y) coordinates from a given contour for the golf ball.

        Args:
        contour ([np.array]): contour from where the coordinate needs to be extracted

        Returns:
        tuple: Returns (x, y) coordinate of the ball
        """

        x = int(np.ceil(np.mean(contour[:, 0])))
        y = int(np.ceil(np.mean(contour[:, 1])))

        return x - 1, y - 1

    def applyGrayscale(self, img, out_dir=None):
        """
        Applies grayscale on the given image.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns the original image with grayscale applied on it
        """

        img_copy = img.copy()
        img_new = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_grayscale.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def applyBitwiseNot(self, img, out_dir=None):
        """
        Applies bitwise not on the given image (inverting the colors).

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns the original image with inverted colors
        """

        img_copy = img.copy()
        img_new = cv2.bitwise_not(img_copy)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_bitwise_not.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def applyErode(self, img, ksize, out_dir=None):
        """
        Applies erode on the given image in order to strengthen contours.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            ksize (tuple): Size of the kernel which should be used in the dilate function
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns the original image with erode applied on it
        """

        img_copy = img.copy()

        kernel = np.ones(ksize)
        img_new = cv2.erode(img_copy, kernel)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_erode.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def applyAdaptiveThreshold(self, img, blockSize, C, maxValue=255, out_dir=None):
        """
        Applies adaptive threshold detection on the given image in order to find contours.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            blockSize (Int): cv2 adaptiveThreshold parameter
            C (Int): cv2 adaptiveThreshold parameter
            maxValue (Int): cv2 adaptiveThreshold parameter
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns the original image with adaptive threshold detection applied on it
        """

        img_copy = img.copy()
        img_new = cv2.adaptiveThreshold(img_copy, maxValue,
                                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, blockSize, C)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_adaptive_threshold.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def applyDilate(self, img, ksize, out_dir=None):
        """
        Applies dilate on the given image in order to strengthen and connect close contours.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            ksize (tuple): Size of the kernel which should be used in the dilate function
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns the original image with dilate applied on it
        """

        img_copy = img.copy()

        kernel = np.ones(ksize)
        img_new = cv2.dilate(img_copy, kernel)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_dilate.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def applySubtract(self, img_before, img_after, out_dir=None):
        """
        Applies subtraction on the given images in order to remove static elements and noise.

        Args:
            img_before ([np.array]): cv2 image taken before shooting the golf ball
            img_after ([np.array]): cv2 image taken after shooting the golf ball
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns an image with contours that are only apparent on the after image and not on the before one
        """

        img_before_copy = img_before.copy()
        img_after_copy = img_after.copy()

        img_new = cv2.subtract(img_after_copy, img_before_copy)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_subtract.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def applyMorphology(self, img, ksize, iterations, out_dir=None):
        """
        Applies morphology on the given image in order to remove unnecessary noise.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            ksize (tuple): Size of the kernel which should be used in the dilate function
            iterations (Int):
            out_dir (string): Directory path where image should be exported after applying mask (only in debug mode)

        Returns:
            Bool: Returns the original image with morphology applied on it
        """

        img_copy = img.copy()

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize)
        img_new = cv2.morphologyEx(img_copy, cv2.MORPH_OPEN, kernel, iterations=iterations)

        if self.debug_mode:
            cv2.imwrite(f"{out_dir}/{self.n_masks_applied}_morphology.jpg", img_new)
            self.n_masks_applied += 1

        return img_new

    def findContourWithLargestArea2(self, img, func):
        """
        Finds contour in cnts with the largest area, the metrics for calculating
        the size of a contour is defined by func.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            func (func): Function for calculating the size of the contour

        Returns:
            Bool: Returns the contour with the largest size.
        """

        img_copy = img.copy()

        cnts, _ = cv2.findContours(img_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        selected_contour = None
        max_size = 0

        for c in cnts:
            c = np.squeeze(c)
            size = func(c)

            if size > max_size:
                selected_contour = c
                max_size = size

        return selected_contour

    def findContourWithLargestArea(self, img, func, num=1):
        """
        Finds contour(s) on image and selects the ones with the largest area, the metrics for calculating
        the size of a contour is defined by func.

        Args:
            img ([np.array]): cv2 image on which the function should be applied
            func (func): Function for calculating the size of the contour
            num: Keep the given number of contours with the largest area, default is 1

        Returns:
            Bool: Returns the contour(s) with the largest size.
        """

        img_copy = img.copy()
        cnts, _ = cv2.findContours(img_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts.sort(key=func)
        cnts = cnts[::-1]  # Reverse array since np.sort sorts by ascending order
        return cnts[:num]

    def selectContourWithLowestPosition(self, cnts):
        """
        Find contour with the lowest vertical position.

        Args:
            cnts ([np.array]): Array of contours

        Returns:
            Bool: Returns the contour with the lowest vertical position.
        """

        # Select the contour that is positioned lower on the image
        selected_contour = cnts[0]
        selected_y = max(np.squeeze(selected_contour)[:, 1])

        for c in cnts[1:]:
            y = max(np.squeeze(c)[:, 1])
            if y > selected_y:
                selected_contour = c
                selected_y = y

        return selected_contour
