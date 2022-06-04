import json
import argparse
from acedistance.helpers.load import loadConfig
from acedistance.main.AceDistance import AceDistance


def main(img_before_path, img_after_path, out_dir, layout_name, debug_mode):
    ad = AceDistance(
        img_before_path=img_before_path,
        img_after_path=img_after_path,
        out_dir=out_dir,
        layout_name=layout_name,
        debug_mode=debug_mode
    )
    ad.run()
    return ad.defaultOutput()


if __name__ == "__main__":
    configParser = loadConfig()

    parser = argparse.ArgumentParser(description='This is the AceChallenge distance estimator entry script.')
    parser.add_argument('img_before_path',
                        type=str,
                        help='Path to the image taken in the beginning of the AceChallenge recording.')

    parser.add_argument('img_after_path',
                        type=str,
                        help='Path to the image taken in the end of the AceChallenge recording.')

    parser.add_argument('-o',
                        '--output',
                        type=str,
                        help='Path of the directory where results should be exported to.\n Default value is '
                             './out/[img-after name] in the current directory.',
                        required=False)

    parser.add_argument('-l',
                        '--layout_name',
                        type=str,
                        help='Name of the grid layout that will be used for the distance estimation. By '
                             'default, the specified layout in config.ini is used.',
                        required=False)

    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Use it to export additional data with the results for debugging purposes.',
                        required=False)

    parser.add_argument('-v', '--version',
                        action='version',
                        version='acedistance {version}'.format(version=configParser['PROGRAM']['VERSION']))

    args = parser.parse_args()

    try:
        # Run algorithm
        main(
            img_before_path=args.img_before_path,
            img_after_path=args.img_after_path,
            out_dir=args.output,
            layout_name=args.layout_name,
            debug_mode=args.debug
        )

    except Exception as e:
        # TODO: Tell Bram that if error is not empty when returned, don't even try to extract other attributes
        r = {'error': e.args[0]}

        # Print out result (endpoint is listening to the printed output)
        print(json.dumps(r))
