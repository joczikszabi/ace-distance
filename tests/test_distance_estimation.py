import pytest
from math import sqrt
from tests.BaseTestClass import BaseTestClass

basecls = BaseTestClass(testcase_name='distance_estimation_test')

DISTANCE_ERROR_LIMIT = 3.1


@pytest.mark.parametrize("layout", ["f4db010a-5dba-4708-b758-24aaad97a48e", "layout1"])
@pytest.mark.parametrize("hole_idx", [[1, 2], [1, 11], [2, 12], [3, 5], [5, 5], [6, 10], [7, 1], [7, 11]])
def test_distance_estimation_on_nodes(layout, hole_idx):
    # Easier tests as residuals are not calculated
    estimator = basecls.get_distance_estimation_object(layout)
    nodes = estimator.gridlayout.getGridNodes()

    for node in [node for row in nodes for node in row if not node == ()]:
        coordinate_hole = nodes[hole_idx[0], hole_idx[1]]
        coordinate_ball = node

        if coordinate_hole == () or coordinate_ball == () or coordinate_ball == coordinate_hole:
            continue

        ball_idx = [(ix, iy) for ix, row in enumerate(nodes) for iy, node in enumerate(row) if node == coordinate_ball][0]
        a = abs(ball_idx[0] - hole_idx[0])
        b = abs(ball_idx[1] - hole_idx[1])

        try:
            dist_expected = round(sqrt(a ** 2 + b ** 2), 2) * estimator.gridlayout.getDistBetweenNodes()
            dist_actual = estimator.estimateDistance(coordinate_hole=coordinate_hole, coordinate_ball=coordinate_ball)

            assert dist_actual == pytest.approx(dist_expected, abs=DISTANCE_ERROR_LIMIT)

        except ValueError as e:
            if e.args[0] == "Position out of grid!":
                continue
            else:
                assert 0
