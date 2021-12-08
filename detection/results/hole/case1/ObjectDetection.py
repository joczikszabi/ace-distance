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
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("0gray.jpg", gray)

        element = np.ones((3,3))
        erode = cv2.erode(gray, element)
        cv2.imwrite("1erodedtresh.jpg", erode)

        thresh = cv2.adaptiveThreshold(erode, 255, cv2.THRESH_BINARY_INV, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 51, 0)
        cv2.imwrite("2thresh.jpg", thresh)

        # Apply edge detection method on the image
        edges = cv2.Canny(thresh, 50, 150, apertureSize = 3)
        cv2.imwrite("3Canny.jpg", edges)

        minLineLength = 50
        maxLineGap = 20
        hough = cv2.HoughLines(thresh, 1, np.pi / 180, 50, None, 50, 10) 
        print(hough)
        #self.draw_lines(hough, erode, 10)  