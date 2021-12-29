import os
import cv2
import numpy as np
import configparser

class ObjectDetection:
    def __init__(self, img_before_path, img_after_path, out_dir):
        
        # Load config data from config file
        configParser = configparser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.txt')
        configParser.read(configFilePath)

        self.img_before_path = img_before_path
        self.img_before = cv2.imread(img_before_path)

        self.img_after_path  = img_after_path
        self.img_after  = cv2.imread(img_after_path)

        self.out_dir = out_dir


    def findAceHole(self):
        # Create directory for outputs
        out_dir = f"{self.out_dir}/hole"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Apply opencv masks for hole detection
        img = self.img_after.copy()
        image_cropped = img[485:img.shape[0]-100, 300:img.shape[1]-300]
        cv2.imwrite(f"{out_dir}/0image_cropped.jpg", image_cropped)

        cv_gray = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"{out_dir}/1gray.jpg", cv_gray)

        element = np.ones((5, 5))
        cv_erode = cv2.erode(cv_gray, element)
        cv2.imwrite(f"{out_dir}/2erode.jpg", cv_erode)

        cv_thresh = cv2.adaptiveThreshold(cv_erode, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)
        cv2.imwrite(f"{out_dir}/3tresh.jpg", cv_thresh)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,10))
        cv_opening = cv2.morphologyEx(cv_thresh, cv2.MORPH_OPEN, kernel, iterations = 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,2))
        cv_opening = cv2.morphologyEx(cv_opening, cv2.MORPH_OPEN, kernel, iterations = 2)
        cv2.imwrite(f"{out_dir}/4morph.jpg", cv_opening)

        # Remove small noise by filtering using contour area
        cnts = cv2.findContours(cv_opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            if cv2.contourArea(c) < 50 or cv2.contourArea(c) > 1000:
                cv2.drawContours(cv_opening, [c], 0, (0,0,0), -1)

        cv2.imwrite(f"{out_dir}/5contour.jpg", cv_opening)

        cv_contours, _ = cv2.findContours(cv_opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        selected_contour = None
        max_area = 0

        for pic, contour in enumerate(cv_contours):
            contour_np = np.asarray([[alma[0][0], alma[0][1]] for alma in contour])
            area = cv2.contourArea(contour)

            x_avg = np.mean(contour_np[:, 0])
            y_max = np.max(contour_np[:, 1])

            # Too close to edge of the image, it cannot be the hole
            if (x_avg < 100 or y_max < 15):
                if area > max_area:
                    continue

            if area > max_area:
                selected_contour = contour
                max_area = area

        if selected_contour is None:
            return None

        cnt2 = np.asarray([[alma[0][0]+300, alma[0][1]+485] for alma in selected_contour])
        x = int(np.ceil(np.mean(cnt2[:, 0])))
        y = max(cnt2[:, 1])

        # Draw the contour on the new mask and perform the bitwise operation
        pos_ace_hole = (x, y-5)
        img_result = cv2.circle(img, pos_ace_hole, 2, (0, 0, 255), 2)
        cv2.imwrite(f"{out_dir}/6result.jpg", img_result)

        return pos_ace_hole


    def findGolfBall(self):
        # Create directory for outputs
        out_dir = f'{self.out_dir}/ball'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        img_after = self.img_after.copy()
        img_after_cropped = img_after[500:img_after.shape[0]-100, 300:img_after.shape[1]-300]
        cv2.imwrite(f"{out_dir}/0image_after_cropped.jpg", img_after_cropped)

        img_before = self.img_before.copy()
        img_before_cropped = img_before[500:img_before.shape[0]-100, 300:img_before.shape[1]-300]
        cv2.imwrite(f"{out_dir}/0image_before_cropped.jpg", img_after_cropped)


        # Get contours and subtract the contours from the before image
        contours_before = self.getContoursForBall(img_before_cropped, out_dir)
        cv2.imwrite(f"{out_dir}/3a_contours_before.jpg", contours_before)

        contours_after  = self.getContoursForBall(img_after_cropped, out_dir)
        cv2.imwrite(f"{out_dir}/3b_contours_after.jpg", contours_after)

        contours = cv2.subtract(contours_after, contours_before)
        cv2.imwrite(f"{out_dir}/3c_contours_substract.jpg", contours)


        # Apply morphology for cleaning up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
        cv_opening = cv2.morphologyEx(contours, cv2.MORPH_OPEN, kernel, iterations = 1)
        cv2.imwrite(f"{out_dir}/4morph.jpg", cv_opening)

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

            if cv2.contourArea(c) > 25 or abs(y_min - y_max) > 6 or abs(x_min - x_max) > 6 or x_avg < 100:
                cv2.drawContours(cv_opening, [c], 0, (0,0,0), -1)

        cv2.imwrite(f"{out_dir}/5contour.jpg", cv_opening)


        # --------------------------------------------------------------------
        # brief: The algorithm chooses the contour with the largest area

        # TODO: Compare the after image with the before one, substract the
        #       similarities i.e previous golf ball, stationary noise etc. and
        #       find the contour with the largest area
        
        contours, hierarchy = cv2.findContours(cv_opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        selected_contour = None
        max_area = 0

        for _, contour in enumerate(contours):
            contour_np = np.asarray([[c[0][0], c[0][1]] for c in contour])
            area = cv2.contourArea(contour)

            x_avg = np.mean(contour_np[:, 0])
            y_avg = np.mean(contour_np[:, 1])

            if area > max_area:
                selected_contour = contour
                max_area = area

        # --------------------------------------------------------------------
        

        # Create a new mask for the result image
        if selected_contour is not None:
            cnt2 = np.asarray([[c[0][0]+300, c[0][1]+500] for c in selected_contour])
            x = int(np.ceil(np.mean(cnt2[:, 0])))
            y = int(np.ceil(np.mean(cnt2[:, 1])))

            # Draw the contour on the new mask and perform the bitwise operation
            #res = cv2.drawContours(image, [cnt2],-1, 255, -1)
            pos_ball = (x, y)
            img_result = cv2.circle(img_after, pos_ball, 2, (0, 0, 255), 2)
            cv2.imwrite(f"{out_dir}/6result.jpg", img_result)

            return pos_ball

        return None


    def getContoursForBall(self, img, out_dir):
        cv_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"{out_dir}/1gray.jpg", cv_gray)

        _, cv_thresh = cv2.threshold(cv_gray, 230, 255, cv2.THRESH_BINARY)

        # Remove small noise by filtering using contour area
        cnts = cv2.findContours(cv_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # If previous threshold detection didn't find any contours, try to lower
        # the treshold range
        if not cnts:
            _, cv_thresh = cv2.threshold(cv_gray, 190, 255, cv2.THRESH_BINARY)

        return cv_thresh
