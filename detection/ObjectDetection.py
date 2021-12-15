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
        image_orig = self.img.copy()
        image = image_orig[500:self.img.shape[0]-100, 300:self.img.shape[1]-300]
        cv2.imwrite("image.jpg", image)

        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite("0gray.jpg", gray)

        element = np.ones((4, 4))
        erode = cv2.erode(gray, element)
        cv2.imwrite("01erode.jpg", erode)

        ret, thresh = cv2.threshold(erode,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        cv2.imwrite("1tresh.jpg", thresh)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,8))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)
        cv2.imwrite("2morph.jpg", opening)

        # Combine surrounding noise with ROI
        kernel = np.ones((3,3),np.uint8)
        dilate = cv2.dilate(opening, kernel, iterations=3)
        cv2.imwrite("3dilate.jpg", dilate)

        #Crop bottom
        cropped = dilate[50:dilate.shape[0]-300, 0:dilate.shape[1]]
        cv2.imwrite("4cropped.jpg", cropped)

        contours, hierarchy = cv2.findContours(cropped, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnt = max(contours, key=cv2.contourArea)

        # Create a new mask for the result image
        h, w = image.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        cnt2 = np.asarray([[alma[0][0]+300, alma[0][1]+550] for alma in cnt])

        x = int(np.ceil(np.mean(cnt2[:, 0])))
        y = max(cnt2[:, 1]) 

        print(f"{x},{y}")

        # Draw the contour on the new mask and perform the bitwise operation
        #res = cv2.drawContours(image, [cnt2],-1, 255, -1)
        res = cv2.circle(image_orig, (x+1,y-5), 2, (0, 0, 255), 2)
        cv2.imwrite("6result.jpg", res)