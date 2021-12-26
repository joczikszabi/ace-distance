import os
import cv2
import numpy as np
import configparser

class ObjectDetection:
    def __init__(self, img_path):
        
        # Load config data from config file
        configParser = configparser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.txt')
        configParser.read(configFilePath)

        self.img_path = img_path
        self.img = cv2.imread(img_path)
        self.img_name,_ = os.path.splitext(os.path.basename(img_path))  


    def findAceHole2(self, out_dir):
        # Create directory for outputss
        out_dir = f"{out_dir}/hole"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        image_orig = self.img.copy()
        image = image_orig[485:self.img.shape[0]-100, 300:self.img.shape[1]-300]
        cv2.imwrite(f"{out_dir}/0image.jpg", image)

        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"{out_dir}/1gray.jpg", gray)

        element = np.ones((5, 5))
        erode = cv2.erode(gray, element)
        cv2.imwrite(f"{out_dir}/2erode.jpg", erode)

        thresh = cv2.adaptiveThreshold(erode,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,51,9)
        cv2.imwrite(f"{out_dir}/3tresh.jpg", thresh)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,10))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,2))
        opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel, iterations = 2)
        cv2.imwrite(f"{out_dir}/4morph.jpg", opening)

        # Remove small noise by filtering using contour area
        cnts = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            if cv2.contourArea(c) < 50 or cv2.contourArea(c) > 1000:
                cv2.drawContours(opening,[c], 0, (0,0,0), -1)

        cv2.imwrite(f"{out_dir}/5contour.jpg", opening)

        contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        selected_contour = None
        max_area = 0

        for pic, contour in enumerate(contours):
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

        # Create a new mask for the result image
        cnt2 = np.asarray([[alma[0][0]+300, alma[0][1]+485] for alma in selected_contour])
        x = int(np.ceil(np.mean(cnt2[:, 0])))
        y = max(cnt2[:, 1])

        # Draw the contour on the new mask and perform the bitwise operation
        res = cv2.circle(image_orig, (x,y-5), 2, (0, 0, 255), 2)
        cv2.imwrite(f"{out_dir}/6result.jpg", res)
        return (x,y-10)


    def findGolfBall(self, img_before_path, out_dir):
        # Create directory for outputs
        out_dir = f'{out_dir}/ball'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        image_orig = self.img.copy()
        image = image_orig[500:self.img.shape[0]-100, 300:self.img.shape[1]-300]
        cv2.imwrite(f"{out_dir}/0image.jpg", image)

        image_before = cv2.imread(img_before_path)
        image_before = image_before[500:image_before.shape[0]-100, 300:image_before.shape[1]-300]


        # Get contours and subtract the contours from the before image
        contours_before = self.getContoursForBall(image_before, out_dir)
        cv2.imwrite(f"{out_dir}/3a_contours_before.jpg", contours_before)

        contours_after  = self.getContoursForBall(image, out_dir)
        cv2.imwrite(f"{out_dir}/3b_contours_after.jpg", contours_after)

        contours = cv2.subtract(contours_after, contours_before)
        cv2.imwrite(f"{out_dir}/3c_contours_substract.jpg", contours)


        # Apply morphology for cleaning up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
        opening = cv2.morphologyEx(contours, cv2.MORPH_OPEN, kernel, iterations = 1)
        cv2.imwrite(f"{out_dir}/4morph.jpg", opening)

        # Remove small noise by removing contours with too large or small area
        cnts = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            contour_np = np.asarray([[alma[0][0], alma[0][1]] for alma in c])
            x_min = np.min(contour_np[:, 0])
            x_max = np.max(contour_np[:, 0])
            x_avg = np.mean(contour_np[:, 0])

            y_min = np.min(contour_np[:, 1])
            y_max = np.max(contour_np[:, 1])
            y_avg = np.mean(contour_np[:, 1])

            if cv2.contourArea(c) > 25 or abs(y_min - y_max) > 6 or abs(x_min - x_max) > 6 or x_avg < 100:
                cv2.drawContours(opening,[c], 0, (0,0,0), -1)

        cv2.imwrite(f"{out_dir}/5contour.jpg", opening)


        # --------------------------------------------------------------------
        # brief: The algorithm chooses the contour with the largest area

        # TODO: Compare the after image with the before one, substract the
        #       similarities i.e previous golf ball, stationary noise etc. and
        #       find the contour with the largest area
        
        contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        selected_contour = None
        max_area = 0

        for pic, contour in enumerate(contours):
            contour_np = np.asarray([[alma[0][0], alma[0][1]] for alma in contour])
            area = cv2.contourArea(contour)

            x_avg = np.mean(contour_np[:, 0])
            y_avg = np.mean(contour_np[:, 1])

            if area > max_area:
                selected_contour = contour
                max_area = area

        # --------------------------------------------------------------------
        

        # Create a new mask for the result image
        if selected_contour is not None:
            cnt2 = np.asarray([[alma[0][0]+300, alma[0][1]+500] for alma in selected_contour])
            x = int(np.ceil(np.mean(cnt2[:, 0])))
            y = int(np.ceil(np.mean(cnt2[:, 1])))

            # Draw the contour on the new mask and perform the bitwise operation
            #res = cv2.drawContours(image, [cnt2],-1, 255, -1)
            res = cv2.circle(image_orig, (x,y), 2, (0, 0, 255), 2)
            cv2.imwrite(f"{out_dir}/6result.jpg", res)

            return (x,y)

        return None


    def getContoursForBall(self, image, out_dir):
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"{out_dir}/1gray.jpg", gray)

        _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
        cv2.imwrite(f"{out_dir}/2tresh.jpg", thresh)

        # Remove small noise by filtering using contour area
        cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        if not cnts:
            _, thresh = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
            cv2.imwrite(f"{out_dir}/2btresh.jpg", thresh)

        return thresh
