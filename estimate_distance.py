import sys
import cv2
import json
import os.path
import configparser
from main.ObjectDetection import ObjectDetection
from main.DistanceEstimation import DistanceEstimation


def main(img_before_path, img_after_path, out_dir='', grid_layout=''):
    # Load config data from config file
    configParser = loadConfig()
    version = configParser['PROGRAM']['VERSION']

    if grid_layout == '':
        # Load config data from config file
        grid_layout = configParser['GRID']['LAYOUT_NAME']

    if not os.path.isfile(img_before_path):
        output = defaultOutput(version,
                               img_before_path,
                               img_after_path,
                               err_msg=f'Image (before) not found on path: {img_before_path}')
        emitAndSaveOutput(output, out_dir)
        return output

    if os.path.isfile(img_after_path):
        img_after = cv2.imread(img_after_path)
    else:
        output = defaultOutput(version,
                               img_before_path,
                               img_after_path,
                               err_msg=f'Image (after) not found on path: {img_after_path}')
        emitAndSaveOutput(output, out_dir)
        return output

    # Create output directory if not supplied
    image_name = os.path.splitext(os.path.basename(img_after_path))[0]
    if out_dir == '':
        out_dir = f"./out/{image_name}"

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Run object detection
    pos_hole, pos_ball = runObjectDetection(img_before_path, img_after_path,
                                            debug_mode=True, out_dir=out_dir, grid_layout=grid_layout)

    # Run distance estimation
    try:
        dist = runDistanceEstimation(img_after, pos_ball, pos_hole, grid_layout=grid_layout)
    except ValueError:
        output = defaultOutput(version,
                               img_before_path,
                               img_after_path,
                               err_msg="Error occurred in estimateDistance")
        emitAndSaveOutput(output, out_dir)
        return output

    # Export result image if distance is calculated
    if dist:
        # Save result image with the distance rendered on it
        saveResultImg(img_after, pos_ball, pos_hole, dist, out_dir)

    # Define output object
    output = defaultOutput(version,
                           img_before_path,
                           img_after_path,
                           distance=dist,
                           is_hole_detected=pos_hole is not None,
                           is_ball_detected=pos_ball is not None,
                           results_path=os.path.abspath(f"{out_dir}/result.jpg") if dist else None)

    emitAndSaveOutput(output, out_dir)
    return output


def loadConfig():
    # Load config data from config file
    configParser = configparser.ConfigParser()
    configFilePath = os.path.join(os.path.dirname(__file__), 'config', 'config.txt')
    configParser.read(configFilePath)

    return configParser


def runObjectDetection(img_before_path, img_after_path, debug_mode, out_dir, grid_layout):
    # Make an instance of the ObjectDetection classes and run the detection algorithm
    det = ObjectDetection(img_before_path, img_after_path, debug_mode=debug_mode, out_dir=out_dir,
                          grid_layout=grid_layout)
    pos_hole = det.findAceHole()
    pos_ball = det.findGolfBall()

    return pos_hole, pos_ball


def runDistanceEstimation(img_after, pos_ball, pos_hole, grid_layout):
    # Make an instance of the DistanceEstimation class and run the estimator algorithm
    estimator = DistanceEstimation(grid_layout=grid_layout)
    dist = estimator.estimateDistance(pos_ball, pos_hole, img_after)

    return dist


def defaultOutput(version, img_before_path, img_after_path, distance=None,
                  is_hole_detected=None, is_ball_detected=None,
                  results_path=None, err_msg=''):
    output = {
        "version": version,
        "distance": distance,
        "is_hole_detected": is_hole_detected,
        "is_ball_detected": is_ball_detected,
        "results_path": results_path,
        "img_before_path": img_before_path,
        "img_after_path": img_after_path,
        "error": err_msg
    }

    return output


def emitAndSaveOutput(output, out_dir):
    # Print out result (endpoint is listening to the printed output)
    output_json = json.dumps(output)
    print(output_json)

    # Save json for logging purposes
    with open(f'{out_dir}/results.json', 'w') as f:
        json.dump(output, f)


def saveResultImg(img, pos_ball, pos_hole, dist, out_dir):
    cv2.line(img, pos_ball, pos_hole, (255, 0, 0), 1)
    cv2.putText(img, f"{str(dist)}m",
                (int((pos_ball[0] + pos_hole[0]) / 2) - 75, int((pos_ball[1] + pos_hole[1]) / 2 - 25)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imwrite(f"{out_dir}/result.jpg", img)


if __name__ == "__main__":
    if len(sys.argv) > 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 3:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2])
