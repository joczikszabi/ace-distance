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


    def draw_lines(self, hough, image, nlines):
        n_x, n_y=image.shape
        print(hough[0])
        #convert to color image so that you can see the lines
        draw_im = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        for (rho, theta) in hough[0][:nlines]:
            print(f"rho,theta({rho}, {theta})")
            try:
                x0 = np.cos(theta)*rho
                y0 = np.sin(theta)*rho
                pt1 = ( int(x0 + (n_x+n_y)*(-np.sin(theta))), int(y0 + (n_x+n_y)*np.cos(theta)) )
                pt2 = ( int(x0 - (n_x+n_y)*(-np.sin(theta))), int(y0 - (n_x+n_y)*np.cos(theta)) )
                alph = np.arctan( (pt2[1]-pt1[1])/( pt2[0]-pt1[0]) )
                alphdeg = alph * 180 / np.pi

                print(f"({pt1}, {pt2})")

                #OpenCv uses weird angle system, see: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
                if abs( np.cos( alph - 180 )) > 0.8: #0.995:
                    cv2.line(draw_im, pt1, pt2, (255,0,0), 2)
                if rho > 0 and abs( np.cos( alphdeg - 90)) > 0.7:
                    cv2.line(draw_im, pt1, pt2, (0,0,255), 2)    
            except:
                pass

        cv2.imwrite("3HoughLines.png", draw_im, [cv2.IMWRITE_PNG_COMPRESSION, 12])   

            
    def findAceHole(self):
        image = self.img.copy()
        image = image[500:self.img.shape[0]-100, 300:self.img.shape[1]-300]
        cv2.imwrite("image.jpg", image)
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite("0gray.jpg", gray)

        element = np.ones((6,6))
        erode = cv2.erode(gray, element)
        cv2.imwrite("1erodedtresh.jpg", erode)

        # adaptive threshold
        #thresh = cv2.adaptiveThreshold(erode,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,51,9)
        #cv2.imwrite("2thresh.jpg", thresh)

        # Fill rectangular contours
        #cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #vcnts = cnts[0] if len(cnts) == 2 else cnts[1]
        #for c in cnts:
        #    cv2.drawContours(thresh, [c], -1, (255,255,255), -1)

        # Morph open
        #kernel = np.ones((6,2),np.uint8)
        #opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=4)
        #cv2.imwrite("3mop.jpg", opening)


        # blur
        blur = cv2.GaussianBlur(erode, (0,0), sigmaX=125, sigmaY=125)
        cv2.imwrite("2blur.jpg", blur)

        # divide
        divide = cv2.divide(gray, blur, scale=255)
        cv2.imwrite("3divide.jpg", divide)

        # otsu threshold
        thresh = cv2.threshold(divide, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        cv2.imwrite("4tresh.jpg", thresh)

        # apply morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,4))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite("5morph.jpg", morph)

        # Draw rectangles, the 'area_treshold' value was determined empirically
        cnts = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        area_treshold = 4000
        for c in cnts:
            if cv2.contourArea(c) > area_treshold :
              x,y,w,h = cv2.boundingRect(c)
              cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)

        cv2.imwrite("result.jpg", image)


        minLineLength = 50
        maxLineGap = 20
        #hough = cv2.HoughLines(thresh, 1, np.pi / 180, 50, None, 50, 10) 
        #print(hough)
        #self.draw_lines(hough, erode, 10) 

    def findAceHole2(self):
        # Create directory for outputs
        out_dir = f"./tmp/{self.img_name}"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_dir = f"./tmp/{self.img_name}/hole"
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



        #Crop bottom
        #cropped = dilate[50:dilate.shape[0]-300, 0:dilate.shape[1]]
        #cv2.imwrite("./tmp/6cropped.jpg", cropped)

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
        #res = cv2.drawContours(image, [cnt2],-1, 255, -1)
        res = cv2.circle(image_orig, (x,y-5), 2, (0, 0, 255), 2)
        cv2.imwrite(f"{out_dir}/6result.jpg", res)
        return (x,y-5)


    def findGolfBall(self):
        # Create directory for outputs
        out_dir = f"./tmp/{self.img_name}"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_dir = f"./tmp/{self.img_name}/ball"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        image_orig = self.img.copy()
        image = image_orig[500:self.img.shape[0]-100, 300:self.img.shape[1]-300]
        cv2.imwrite(f"{out_dir}/0image.jpg", image)

        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"{out_dir}/1gray.jpg", gray)

        #whiten = cv2.convertScaleAbs(gray, alpha=1.15, beta=1.5)
        #cv2.imwrite(f"{out_dir}/2whiten.jpg", whiten)

        _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
        cv2.imwrite(f"{out_dir}/3tresh.jpg", thresh)

        # Remove small noise by filtering using contour area
        cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        if not cnts:
            _, thresh = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
            cv2.imwrite(f"{out_dir}/3btresh.jpg", thresh)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)
        cv2.imwrite(f"{out_dir}/4morph.jpg", opening)

        # Remove small noise by filtering using contour area
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
            print(f"area:{cv2.contourArea(c)}")

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