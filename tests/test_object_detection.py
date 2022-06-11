import pytest

from tests.BaseTestClass import BaseTestClass
from tests.helpers.get_testcases import get_testcases


basecls = BaseTestClass(testcase_name='object_detection_test')


@pytest.mark.parametrize('testcase', get_testcases(basecls.data_dir))
def test_hole_detection(testcase):
    det = basecls.get_detection_object(testcase)
    pos_hole = det.findAceHole()

    # First check if a position was found when there is one
    assert (pos_hole is not None) == (not testcase["hole_position"] == [])

    # Next check if the location of the found object is good
    assert pos_hole == pytest.approx(testcase["hole_position"], abs=15)


@pytest.mark.parametrize('testcase', get_testcases(basecls.data_dir))
def test_ball_detection(testcase):
    det = basecls.get_detection_object(testcase)
    pos_ball = det.findGolfBall()

    # First check if a position was found when there is one
    assert (pos_ball is not None) == (not testcase["ball_position"] == [])

    # Next check if the location of the found object is good
    if pos_ball:
        assert pos_ball == pytest.approx(testcase["ball_position"], abs=15)
