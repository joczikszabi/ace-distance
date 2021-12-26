# Renders the grid points on the given image
#
# Parameters:
# -img: Image on which the grid layout is to be rendered
# -nodes: Grid layout configuration (stored at /config/grid.json) as a dictionry
#
# Returns:
# - Image in opencv format with the grid nodes rendered on it

import cv2

def plot_grid(img, nodes): 
	for row in nodes:
		for node in row:
			if not node == ():
				# Radius of circle
				radius = 5
				  
				# Red color in BGR
				color = (0, 0, 255)
				  
				# Line thickness of -1 px
				thickness = -1

				# Draw a circle of red color of thickness -1 px
				cv2.circle(img, node, radius, color, thickness)

	return img