import os
import pytest

from tests.BaseTestClass import BaseTestClass
from tests.get_testcases import get_testcases
import estimate_distance

basecls = BaseTestClass(testcase_name='entry_script_test')


@pytest.mark.parametrize('testcase', get_testcases(basecls.dataDir()))
def test_entry_script_returned_data(testcase):
    output_path = basecls.get_output_path(testcase['layout'], testcase['img_name'])
    actual_result = estimate_distance.main(img_before_path=basecls.get_img_before_path(testcase['img_name']),
                                           img_after_path=basecls.get_img_after_path(testcase['img_name']),
                                           out_dir=output_path,
                                           grid_layout=testcase['layout'],
                                           debug_mode=False)

    assert actual_result['is_hole_detected'] == testcase['is_hole_detected']
    assert actual_result['is_ball_detected'] == testcase['is_ball_detected']
    assert actual_result['layout_name'] == testcase['layout']

    if testcase['is_hole_detected'] and testcase['is_ball_detected']:
        assert actual_result['distance'] is not None
        assert actual_result['results_path'] == os.path.abspath(f"{output_path}/result.jpg")

    assert actual_result['img_before_path'] == basecls.get_img_before_path(testcase['img_name'])
    assert actual_result['img_after_path'] == basecls.get_img_after_path(testcase['img_name'])
    assert actual_result['error'].startswith(testcase['error'])


@pytest.mark.parametrize('testcase', get_testcases(basecls.dataDir()))
def test_results_exported(testcase):
    output_path = basecls.get_output_path(testcase['layout'], testcase['img_name'])
    estimate_distance.main(img_before_path=basecls.get_img_before_path(testcase['img_name']),
                           img_after_path=basecls.get_img_after_path(testcase['img_name']),
                           out_dir=output_path,
                           grid_layout=testcase['layout'],
                           debug_mode=False)

    if testcase['is_hole_detected'] and testcase['is_ball_detected']:
        assert os.path.isfile(f'{output_path}/result.jpg')

    assert os.path.isfile(f'{output_path}/results.json')
