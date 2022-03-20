import sys
import cv2
import json
import os.path

from main.ObjectDetection import ObjectDetection
from main.DistanceEstimation import DistanceEstimation


def main(img_before_path, img_after_path, out_dir='', grid_layout=''):
    if not os.path.isfile(img_before_path):
        exit(f"Image (before) not found on path: {img_before_path}")

    if os.path.isfile(img_after_path):
        img_after = cv2.imread(img_after_path)
    else:
        exit(f"Image (after) not found on path: {img_after_path}")

    # Create output directory if not supplied
    image_name = os.path.splitext(os.path.basename(img_after_path))[0]
    if out_dir == '':
        out_dir = f"./out/{image_name}"

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Make an instance of the ObjectDetection classes and run the detection algorithm
    det = ObjectDetection(img_before_path, img_after_path, debug_mode=True, out_dir=out_dir, grid_layout=grid_layout)
    pos_hole = det.findAceHole()
    pos_ball = det.findGolfBall()

    # Make an instance of the DistanceEstimation class and run the estimator algorithm
    estimator = DistanceEstimation(generate_dummy=False, grid_layout=grid_layout)
    dist = estimator.estimateDistance(pos_ball, pos_hole, img_after)

    if dist:
        # Save result image with the distance rendered on it
        cv2.line(img_after, pos_ball, pos_hole, (255, 0, 0), 1)
        cv2.putText(img_after, f"{str(dist)}m",
                    (int((pos_ball[0] + pos_hole[0]) / 2) - 75, int((pos_ball[1] + pos_hole[1]) / 2 - 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imwrite(f"{out_dir}/result.jpg", img_after)

    # Define output object
    output = {
        "distance": dist,
        "is_hole_detected": pos_hole is not None,
        "is_ball_detected": pos_ball is not None,
        "is_distance_calculated": dist is not None,
        "results_path": os.path.abspath(f"{out_dir}/result.jpg") if dist else None,
        "img_before": img_before_path,
        "img_after": img_after_path
    }

    # Print out result
    output_json = json.dumps(output)
    print(output_json)

    # Save json for logging purposes
    with open(f'{out_dir}/results.json', 'w') as f:
        json.dump(output, f)

    return output


if __name__ == "__main__":
    if len(sys.argv) > 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 3:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2])

