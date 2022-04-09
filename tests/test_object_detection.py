import pytest

from tests.BaseTestClass import BaseTestClass
from tests.get_testcases import get_testcases


basecls = BaseTestClass(testcase_name='object_detection_test')


@pytest.mark.parametrize('testcase', get_testcases(basecls.dataDir()))
def test_hole_detection(testcase):
    det = basecls.detectionObject(testcase)
    pos_hole = det.findAceHole()

    assert (pos_hole is not None) == testcase["is_hole_detected"]


@pytest.mark.parametrize('testcase', get_testcases(basecls.dataDir()))
def test_ball_detection(testcase):
    det = basecls.detectionObject(testcase)
    pos_ball = det.findGolfBall()

    assert (pos_ball is not None) == testcase["is_ball_detected"]
