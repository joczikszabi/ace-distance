import os
import cv2
import math
import numpy as np


class ObjectDetection:
    def __init__(self, img_before_path, img_after_path, gridlayout, out_dir, debug_mode=False):
        self.gridlayout = gridlayout

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
            # Create directory for outputs
            self.out_dir_hole = f"{self.out_dir}/hole"
            if not os.path.exists(self.out_dir_hole):
                os.makedirs(self.out_dir_hole)

            self.out_dir_ball = f'{self.out_dir}/ball'
            if not os.path.exists(self.out_dir_ball):
                os.makedirs(self.out_dir_ball)

    def findAceHole(self):
        # Apply opencv masks for hole detection
        img = self.img_after.copy()

        # Crop image
        x0 = self.gridlayout.layout['mask']['hole']['crop']['x0']
        x1 = self.gridlayout.layout['mask']['hole']['crop']['x1']
        y0 = self.gridlayout.layout['mask']['hole']['crop']['y0']
        y1 = self.gridlayout.layout['mask']['hole']['crop']['y1']

        image_cropped = img[y0:y1, x0:x1]
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/0image_cropped.jpg", image_cropped)

        # Apply grayscale
        cv_gray = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2GRAY)
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

        # Remove contours that are too small or too large
        cnts = cv2.findContours(cv_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            if cv2.contourArea(c) < 100:
                cv2.drawContours(cv_dilate, [c], 0, (0, 0, 0), -1)

        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/6contour.jpg", cv_dilate)

        cv_contours, _ = cv2.findContours(cv_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        selected_contour = None
        max_area = 0

        for pic, contour in enumerate(cv_contours):
            contour_np = np.asarray([[alma[0][0], alma[0][1]] for alma in contour])
            area = cv2.contourArea(contour)

            x_min = np.min(contour_np[:, 0])
            x_max = np.max(contour_np[:, 0])
            x_avg = np.mean(contour_np[:, 0])

            y_min = np.min(contour_np[:, 1])
            y_max = np.max(contour_np[:, 1])

            # Too close to edge of the image, it cannot be the hole
            img_height = y1 - y0
            height_width_ratio = (y_max - y_min) / (x_max - x_min)
            if (x_avg < 50 or x_avg > (x1 - 50) or y_min > img_height - 15 or height_width_ratio < 2):
                if area > max_area:
                    continue

            if area > max_area:
                selected_contour = contour
                max_area = area

        if selected_contour is None:
            return None

        cnt2 = np.asarray([[alma[0][0]+x0, alma[0][1] + y0] for alma in selected_contour])
        y = max(cnt2[:, 1]) - 5
        x = int(np.mean(np.array([v for v in cnt2 if v[1] == y])[:, 0]))

        # Draw the contour on the new mask and perform the bitwise operation
        pos_ace_hole = (x, y)
        img_result = cv2.circle(img, pos_ace_hole, 2, (0, 0, 255), 2)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_hole}/7result.jpg", img_result)

        return pos_ace_hole

    def findGolfBall(self):
        img_after = self.img_after.copy()

        # Crop before and after images
        x0 = self.gridlayout.layout['mask']['ball']['crop']['x0']
        x1 = self.gridlayout.layout['mask']['ball']['crop']['x1']
        y0 = self.gridlayout.layout['mask']['ball']['crop']['y0']
        y1 = self.gridlayout.layout['mask']['ball']['crop']['y1']

        img_after_cropped = img_after[y0:y1, x0:x1]
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/0image_after_cropped.jpg", img_after_cropped)

        img_before = self.img_before.copy()
        img_before_cropped = img_before[y0:y1, x0:x1]
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/0image_before_cropped.jpg", img_before_cropped)

        # Get contours and subtract the contours from the before image
        contours_before = self.getContoursForBall(img_before_cropped)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3a_contours_before.jpg", contours_before)

        # Enlarge found contours on before image for subtraction
        element = np.ones((4, 4))
        contours_before_dilate = cv2.dilate(contours_before, element)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3a_contours_before_dilate.jpg", contours_before_dilate)

        contours_after = self.getContoursForBall(img_after_cropped)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3b_contours_after.jpg", contours_after)

        # Enlarge found contours on after image for subtraction (not as much as on the before image)
        element = np.ones((3, 2))
        contours_after_dilate = cv2.dilate(contours_after, element)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3b_contours_after_dilate.jpg", contours_after_dilate)

        contours = cv2.subtract(contours_after_dilate, contours_before_dilate)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/3c_contours_substract.jpg", contours)

        # Apply morphology for cleaning up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cv_opening = cv2.morphologyEx(contours, cv2.MORPH_OPEN, kernel, iterations=1)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/4morph.jpg", cv_opening)

        # Remove small noise by removing contours with too large or small area
        cnts = cv2.findContours(cv_opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            contour_np = np.asarray([[cc[0][0], cc[0][1]] for cc in c])
            x_min = np.min(contour_np[:, 0])
            x_max = np.max(contour_np[:, 0])
            x_avg = np.mean(contour_np[:, 0])

            y_min = np.min(contour_np[:, 1])
            y_max = np.max(contour_np[:, 1])
            y_avg = np.mean(contour_np[:, 1])

            if cv2.contourArea(c) < 3 or cv2.contourArea(c) > 30 or abs(y_min - y_max) > 10 or abs(x_min - x_max) > 10 \
                    or x_avg < 100 or y_avg < 5:
                cv2.drawContours(cv_opening, [c], 0, (0, 0, 0), -1)

        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/5contour.jpg", cv_opening)

        # --------------------------------------------------------------------
        # brief: The algorithm chooses the contour with the largest area

        # TODO: Compare the after image with the before one, substract the
        #       similarities i.e previous golf ball, stationary noise etc. and
        #       find the contour with the largest area

        contours, hierarchy = cv2.findContours(cv_opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        selected_contour = None
        max_area = 0

        for _, contour in enumerate(contours):
            _, radius = cv2.minEnclosingCircle(contour)
            area = math.pi * radius

            if area > max_area:
                selected_contour = contour
                max_area = area

        # --------------------------------------------------------------------

        # Create a new mask for the result image
        if selected_contour is not None:
            cnt2 = np.asarray([[c[0][0] + x0, c[0][1] + y0] for c in selected_contour])
            x = int(np.ceil(np.mean(cnt2[:, 0])))
            y = int(np.ceil(np.mean(cnt2[:, 1])))

            # Draw the contour on the new mask and perform the bitwise operation
            # res = cv2.drawContours(image, [cnt2],-1, 255, -1)
            pos_ball = (x, y)
            img_result = cv2.circle(img_after, pos_ball, 2, (0, 0, 255), 2)
            if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/6result.jpg", img_result)

            return pos_ball

        return None

    def getContoursForBall(self, img):
        cv_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.debug_mode: cv2.imwrite(f"{self.out_dir_ball}/1gray.jpg", cv_gray)

        thrld_min = self.gridlayout.layout['mask']['ball']['threshold']['min']
        thrld_max = self.gridlayout.layout['mask']['ball']['threshold']['max']
        _, cv_thresh = cv2.threshold(cv_gray, thrld_min, thrld_max, cv2.THRESH_BINARY)

        # Remove small noise by filtering using contour area
        cnts = cv2.findContours(cv_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # If previous threshold detection didn't find any contours, try to lower
        # the threshold range
        if not cnts:
            thrld_min_fallback = self.gridlayout.layout['mask']['ball']['threshold']['fallback']
            _, cv_thresh = cv2.threshold(cv_gray, thrld_min_fallback, thrld_max, cv2.THRESH_BINARY)

        return cv_thresh
