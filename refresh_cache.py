import os
import cv2
import argparse
from acedistance.helpers.load import loadConfig
from acedistance.helpers.cache import saveCache
from acedistance.main.Grid import GridLayout
from acedistance.main.ObjectDetection import ObjectDetection


def main(img_path, out_dir, layout_name):
    """ Creates or overwrites an existing active cache with the detected hole's position on the given image

    Args:
        img_path (list(str))): List of files to copy
        out_dir (str): Directory where the image with the detected hole position should be exported to
        layout_name (str): Name of the new layout for which the cache should be created
    """

    if not os.path.isfile(img_path):
        print(f'Image not found on path: {img_path}')
        return

    gridlayout = GridLayout(layout_name)
    det = ObjectDetection(img_before_path=img_path,
                          img_after_path=img_path,
                          gridlayout=gridlayout,
                          out_dir=out_dir,
                          debug_mode=False)

    pos_hole = det.findAceHole()
    if pos_hole:
        saveCache(layout_name, pos_hole, overwrite=True)
        img_result = cv2.circle(cv2.imread(img_path), pos_hole, 2, (0, 0, 255), 2)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        cv2.imwrite(f"{out_dir}/hole_position.png", img_result)

    else:
        print("Ace hole was not detected on the provided image.")


if __name__ == "__main__":
    configParser = loadConfig()

    parser = argparse.ArgumentParser(description='This is the AceChallenge distance estimator entry script.')
    parser.add_argument('img_path',
                        type=str,
                        help='Path to the image on which the hole detection should run.')

    parser.add_argument('-o',
                        '--output',
                        type=str,
                        help='Path of the directory where the result image should be exported to.\n Default value is '
                             './cache_hole/[img name] in the current directory.',
                        required=False)

    parser.add_argument('-l',
                        '--layout_name',
                        type=str,
                        help='Name of the grid layout. By default, the specified layout in config.ini is used.',
                        required=False)

    args = parser.parse_args()

    try:
        main(
            img_path=args.img_path,
            out_dir=args.output if args.output else configParser['PROGRAM']['DEFAULT_OUTDIR'],
            layout_name=args.layout_name if args.layout_name else configParser['GRID']['LAYOUT_NAME'],
        )

    except Exception as e:
        print(f'Refreshing cache failed: {e.args[0]}')
