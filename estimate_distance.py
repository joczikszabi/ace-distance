import cv2
import json
import os.path
import argparse
from acedistance.helpers.load import loadConfig
from acedistance.main.Grid import GridLayout
from acedistance.main.ObjectDetection import ObjectDetection
from acedistance.main.DistanceEstimation import DistanceEstimation


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main(img_before_path, img_after_path, out_dir=None, layout_name=None, debug_mode=None):
    # Load config data from config file
    configParser = loadConfig()
    version = configParser['PROGRAM']['VERSION']

    # Set default optional argument values
    out_dir, layout_name, debug_mode = getOptionalArguments(img_after_path=img_after_path,
                                                            out_dir=out_dir,
                                                            layout_name=layout_name,
                                                            debug_mode=debug_mode)

    # Set layout
    gridlayout = GridLayout(layout_name)

    # Check if images exist
    if not os.path.isfile(img_before_path):
        output = defaultOutput(version=version,
                               img_before_path=img_before_path,
                               img_after_path=img_after_path,
                               layout_name=layout_name,
                               results_path=out_dir,
                               err_msg=f'Image (before) not found on path: {img_before_path}')
        emitAndSaveOutput(output, out_dir)
        return output

    if not os.path.isfile(img_after_path):
        output = defaultOutput(version=version,
                               img_before_path=img_before_path,
                               img_after_path=img_after_path,
                               layout_name=layout_name,
                               results_path=out_dir,
                               err_msg=f'Image (after) not found on path: {img_after_path}')
        emitAndSaveOutput(output, out_dir)
        return output

    # OBJECT DETECTION
    # Make an instance of the ObjectDetection classes and run the detection algorithm
    det = ObjectDetection(img_before_path=img_before_path,
                          img_after_path=img_after_path,
                          debug_mode=debug_mode,
                          out_dir=out_dir,
                          layout_name=layout_name)
    pos_hole = det.findAceHole()
    pos_ball = det.findGolfBall()

    # DISTANCE ESTIMATION
    # Make an instance of the DistanceEstimation class and run the estimator algorithm
    try:
        estimator = DistanceEstimation(gridlayout=gridlayout)
        img_after = cv2.imread(img_after_path)
        dist = estimator.estimateDistance(pos_ball, pos_hole, img_after)

    except ValueError as e:
        output = defaultOutput(version=version,
                               img_before_path=img_before_path,
                               img_after_path=img_after_path,
                               layout_name=layout_name,
                               results_path=out_dir,
                               err_msg=e.args[0])
        emitAndSaveOutput(output, out_dir)
        return output

    # Export result image if distance is calculated
    if dist:
        saveResultImg(img_after, pos_ball, pos_hole, dist, out_dir)

    # Define output object
    output = defaultOutput(version=version,
                           img_before_path=img_before_path,
                           img_after_path=img_after_path,
                           layout_name=layout_name,
                           distance=dist,
                           is_hole_detected=pos_hole is not None,
                           is_ball_detected=pos_ball is not None,
                           results_path=os.path.abspath(f"{out_dir}/result.jpg") if dist else out_dir)

    emitAndSaveOutput(output, out_dir)

    return output


def getOptionalArguments(img_after_path, out_dir, layout_name, debug_mode):
    # Set default optional argument values if not set
    image_name = os.path.splitext(os.path.basename(img_after_path))[0]

    if out_dir is None:
        out_dir = f"{configParser['PROGRAM']['DEFAULT_OUTDIR']}/{image_name}"

    if layout_name is None:
        layout_name = configParser['GRID']['LAYOUT_NAME']

    if debug_mode is None:
        debug_mode = bool(int(configParser['PROGRAM']['DEBUG_MODE']))

    return out_dir, layout_name, debug_mode


def defaultOutput(version, img_before_path, img_after_path, layout_name,
                  distance=None, is_hole_detected=None, is_ball_detected=None,
                  results_path=None, err_msg=''):
    output = {
        "version": version,
        "distance": distance,
        "layout_name": layout_name,
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

    # Create out directory if does not exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

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
    configParser = loadConfig()

    # Add argparser arguments
    parser = argparse.ArgumentParser(description='This is the AceChallenge distance estimator entry script.')
    parser.add_argument('img_before_path',
                        type=str,
                        help='(Required) Path to the image taken in the beginning of the AceChallenge recording.')

    parser.add_argument('img_after_path',
                        type=str,
                        help='(Required) Path to the image taken in the end of the AceChallenge recording.')

    parser.add_argument('-o',
                        '--output',
                        type=str,
                        help='(Optional) Path of the directory where results should be exported to.\n Default value is '
                             './out/[img-after name] in the current directory.',
                        required=False)

    parser.add_argument('-l',
                        '--layout_name',
                        type=str,
                        help='(Optional) Name of the grid layout that will be used for the distance estimation. By '
                             'default, the specified layout in config.ini is used.',
                        required=False,
                        default=configParser['GRID']['LAYOUT_NAME'])

    parser.add_argument('-d',
                        '--debug_mode',
                        type=str2bool,
                        help='(Optional) If set to True, additional data is exported along with the results for '
                             'debugging purposes. False by default.',
                        required=False,
                        default=bool(int(configParser['PROGRAM']['DEBUG_MODE'])))

    parser.add_argument('-v', '--version', action='version',
                        version='acedistance {version}'.format(version=configParser['PROGRAM']['VERSION']))

    # Execute the parse_args() method
    args = parser.parse_args()

    try:
        main(img_before_path=args.img_before_path,
             img_after_path=args.img_after_path,
             out_dir=args.output,
             layout_name=args.layout_name,
             debug_mode=args.debug_mode)

    except Exception as e:
        resultspath = args.output if args.output is not None else f"{configParser['PROGRAM']['DEFAULT_OUTDIR']}/{os.path.splitext(os.path.basename(args.img_after_path))[0]}"
        output = defaultOutput(version=configParser['PROGRAM']['VERSION'],
                               img_before_path=args.img_before_path,
                               img_after_path=args.img_after_path,
                               layout_name=args.layout_name,
                               results_path=resultspath,
                               err_msg=e.args[0])
        emitAndSaveOutput(output, resultspath)
