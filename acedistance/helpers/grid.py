import cv2
import numpy as np
from random import randint


def draw_nodes(img_path, nodes, indices_on=True, auto_open=True):
    """ Renders the grid node points on the given image.

    Parameters:
        - img_path (str): Path to the image on which the mask points should be rendered
        - nodes (list(list(list(int))): List of grid node points
        - indices_on (Boolean): Should the row and column indices of the node also be rendered on the image. Default is True.
        - auto_open (Boolean): Should the image be opened automatically after rendering the points. Default is True.

    Returns:
        - cv2 object: Image in opencv format with the grid node points rendered on it
    """

    img = cv2.imread(img_path)

    row_idx = 0
    col_idx = 0

    for row in nodes:
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)

        for node in row:
            if not node == ():
                # Radius of circle
                radius = 4

                # Create a color tuple from the random integers
                color = (r, g, b)

                # Line thickness of -1 px
                thickness = -1

                # Draw a circle of red color of thickness -1 px
                cv2.circle(img, node, radius, color, thickness)

                if indices_on:
                    # Draw column and row number above grid node
                    cv2.putText(img, str((row_idx, col_idx)), (node[0] + 5, node[1] - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)

            col_idx += 1

        col_idx = 0
        row_idx += 1

    if auto_open:
        cv2.imshow('Grid nodes', img)

        # Wait for a key to be pressed to exit
        cv2.waitKey(0)

    return img


def render_commands(img):
    """
    Renders text on the given image regarding the usable commands and events

    Args:
        img (cv2 object): Image on which the text should be rendered

    Returns:
        cv2 object: Image with the rendered text on it
    """

    cv2.putText(img, "Left mouse click: Select next point (not saved yet).", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "Right mouse click: Clear currently selected point.", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "Space: Save selected (or empty) point.", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255),
                1,
                cv2.LINE_AA)


def render_status(img, col_idx, row_idx, n_rows, len_col):
    """
    Renders text on the given image regarding the current status of the node definition including the current
    number of row, column and how many nodes are remaining in the given column.

    Args:
        img (cv2 object): Image on which the text should be rendered
        col_idx (int): Index of the current col
        row_idx (int): Index of the current row
        n_rows (int): Maximum number of rows in the complete grid layout
        len_col (int): Number of nodes that have been selected in the current column

    Returns:
        cv2 object: Image with the rendered text on it
    """

    cv2.putText(img,
                f"Current column: {col_idx + 1}   Current row: {row_idx + 1}    Remaining points in current column: {n_rows - len_col}",
                (10, 714), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                (0, 0, 0), 1, cv2.LINE_AA)


def render_info(img, n_rows, n_cols):
    """
    Renders text on the given image regarding meta information about the current grid layout including the
    maximum number of rows and columns in the complete grid layout.

    Args:
        img (cv2 object): Image on which the text should be rendered
        n_rows (int): Maximum number of rows in the complete grid layout
        n_cols (int): Maximum number of columns in the complete grid layout

    Returns:
        cv2 object: Image with the rendered text on it
    """

    cv2.putText(img, f"Total number of column: {n_cols}   Total number of row: {n_rows}",
                (925, 714), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                (0, 0, 0), 1, cv2.LINE_AA)


def add_transparent_background(img, x, y, w, h, alpha, color):
    """
    Adds a transparent rectangle on the image. The position and size of the rectangle are given as parameters
    as well as its alpha channel and its color.

    Args:
        img (cv2 object): Image on which the text should be rendered
        x (int): Position x of the top left corner of the rectangle
        y (int): Position y of the top left corner of the rectangle
        w (int): Width of the rectangle in terms of pixels
        h (int): Height of the rectangle in terms of pixels
        alpha (float): Value of the alpha channel
        color (int): Color of the rectangle

    Returns:
        cv2 object: Image with the rendered text on it
    """

    sub_img = img[y:y + h, x:x + w]
    rect = np.ones(sub_img.shape, dtype=np.uint8) * color
    res = cv2.addWeighted(sub_img, alpha, rect, 1 - alpha, 1.0)
    img[y:y + h, x:x + w] = res


def set_nodes(img_path, n_rows, n_cols):
    """
    Helper function for setting up the grid node points' positions for a given layout. The function opens the image
    specified by imgs_path and applies the following callbacks to it:
    - Mouse left click: Select a point on the image
    - Mouse right click: Clear currently selected point
    - Space: Save currently selected (or empty) point
    - q: Quit process and return with None

    In every case, an m x n matrix has to be defined where m is given by n_rows and n is given by n_cols. The elements
    of the matrix are tuples (pixel coordinates). Since in most cases the grid layout does not have the same number
    of connection points in each column and row, empty entries are allowed [] to fill the missing entries of the matrix.

    Args:
        img_path (str): Path to the reference image on which the grid layout can be seen on the field
        n_rows (int): Maximum number of rows in the complete grid layout
        n_cols (int): Maximum number of columns in the complete grid layout

    Returns:
        cv2 object: Image with the rendered text on it
    """

    img = cv2.imread(img_path, 1)
    add_transparent_background(img, 0, 0, 1920, 150, 0.3, 0)
    add_transparent_background(img, 0, 700, 1920, 180, 0, 255)
    render_commands(img)
    render_info(img, n_rows, n_cols)

    nodes = np.zeros((n_rows, n_cols), dtype=object)
    col = []
    col_idx = 0
    row_idx = 0

    DEFAULT_NODE_VALUE = ()

    pos = DEFAULT_NODE_VALUE

    def click_event(event, x, y, flags, params):
        nonlocal nodes, col, col_idx, row_idx, pos  # access outer scope variables

        # Listen for left mouse clicks.
        # Users can adjust the selected point
        if event == cv2.EVENT_LBUTTONDOWN:
            pos = (x, y)
            img_tmp = img.copy()
            render_status(img_tmp, col_idx, row_idx, n_rows, len(col))
            cv2.circle(img_tmp, (x, y), 3, (0, 0, 255), -1)
            cv2.imshow('Select node points', img_tmp)

        # Listen for right mouse clicks.
        # Users can remove the selected point
        elif event == cv2.EVENT_RBUTTONDOWN:
            pos = DEFAULT_NODE_VALUE
            img_tmp = img.copy()
            render_status(img_tmp, col_idx, row_idx, n_rows, len(col))
            cv2.imshow('Select node points', img_tmp)

    # Render image
    img_tmp = img.copy()
    render_status(img_tmp, col_idx, row_idx, n_rows, len(col))
    cv2.imshow('Select node points', img_tmp)
    cv2.setMouseCallback('Select node points', click_event)

    while 1:
        key = cv2.waitKey(0)

        if key == ord('q'):
            return None

        # If 'space' is pressed, finalize and save the selected point (or empty point [None, None])
        elif key == 32:
            col.append(pos)

            if pos is not DEFAULT_NODE_VALUE:
                cv2.circle(img, tuple(pos), 3, (0, 0, 255), -1)

            # Reset the position variable
            pos = DEFAULT_NODE_VALUE
            row_idx += 1

        if row_idx == n_rows:
            nodes[:, col_idx] = col
            col_idx += 1
            row_idx = 0
            print(f'Set nodes for column {col_idx}: {col}')
            col = []

        if col_idx == n_cols:
            break

        img_tmp = img.copy()
        render_status(img_tmp, col_idx, row_idx, n_rows, len(col))
        cv2.imshow('Select node points', img_tmp)

    cv2.destroyAllWindows()

    return nodes.tolist()
