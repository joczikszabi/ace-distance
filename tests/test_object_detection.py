import pytest

from tests.BaseTestClass import BaseTestClass
from tests.helpers.get_testcases import get_testcases


basecls = BaseTestClass(testcase_name='object_detection_test')


@pytest.mark.parametrize('testcase', get_testcases(basecls.data_dir))
def test_hole_detection(testcase):
    det = basecls.get_detection_object(testcase)
    pos_hole = det.findAceHole()

    assert (pos_hole is not None) == testcase["is_hole_detected"]


@pytest.mark.parametrize('testcase', get_testcases(basecls.data_dir))
def test_ball_detection(testcase):
    det = basecls.get_detection_object(testcase)
    pos_ball = det.findGolfBall()

    assert (pos_ball is not None) == testcase["is_ball_detected"]
