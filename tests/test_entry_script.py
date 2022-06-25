import os
import pytest

import refresh_cache
import estimate_distance
from acedistance.main.AceDistance import AceDistance
from tests.BaseTestClass import BaseTestClass
from tests.helpers.get_testcases import get_testcases

basecls = BaseTestClass(testcase_name='entry_script_test')


@pytest.mark.parametrize('testcase', get_testcases(basecls.data_dir))
def test_entry_script_returned_data(testcase):
    output_path = basecls.get_output_path(testcase['layout'], testcase['img_name'])
    actual_result = estimate_distance.main(img_before_path=basecls.get_img_before_path(testcase['img_name']),
                                           img_after_path=basecls.get_img_after_path(testcase['img_name']),
                                           out_dir=output_path,
                                           layout_name=testcase['layout'],
                                           debug_mode=False,
                                           use_cache=False)

    assert actual_result['img_before_path'] == basecls.get_img_before_path(testcase['img_name'])
    assert actual_result['img_after_path'] == basecls.get_img_after_path(testcase['img_name'])
    assert actual_result['is_hole_detected'] == testcase['is_hole_detected']
    assert actual_result['is_ball_detected'] == testcase['is_ball_detected']
    assert actual_result['ball_on_the_green'] == testcase['ball_on_the_green']
    assert actual_result['layout_name'] == testcase['layout']
    assert actual_result['error'].startswith(testcase['error'])

    if testcase['is_hole_detected'] and testcase['is_ball_detected'] and not testcase['error']:
        assert actual_result['distance'] is not None and actual_result['distance'] >= 0
        assert actual_result['results_path'] == os.path.abspath(f"{output_path}/result.jpg")

    else:
        assert actual_result['distance'] is None


@pytest.mark.parametrize('testcase', get_testcases(basecls.data_dir))
def test_results_exported(testcase):
    output_path = basecls.get_output_path(testcase['layout'], testcase['img_name'])
    estimate_distance.main(img_before_path=basecls.get_img_before_path(testcase['img_name']),
                           img_after_path=basecls.get_img_after_path(testcase['img_name']),
                           out_dir=output_path,
                           layout_name=testcase['layout'],
                           debug_mode=False,
                           use_cache=False)

    if testcase['is_hole_detected'] and testcase['is_ball_detected'] and not testcase['error']:
        assert os.path.isfile(f'{output_path}/result.jpg')

    assert os.path.isfile(f'{output_path}/result.json')


def test_caching():
    fails_without_caching_img_name = 'a020eea9-8301-4d0f-9813-8bb013b99feb'
    layout = 'f4db010a-5dba-4708-b758-24aaad97a48e'
    output_path = basecls.get_output_path(layout, fails_without_caching_img_name)

    # First test if hole detection fails without using cache caching
    ad = AceDistance(
        img_before_path=basecls.get_img_after_path(fails_without_caching_img_name),
        img_after_path=basecls.get_img_after_path(fails_without_caching_img_name),
        out_dir=output_path,
        layout_name=layout,
        debug_mode=False,
        use_cache=False
    )
    ad.run()

    assert not (ad.pos_hole == pytest.approx([658, 450], abs=15))

    # Now refresh cache using reference image
    reference_img_name = '55151342-8d18-4fe7-a56d-5ca38b7eeed4'
    reference_img_path = basecls.get_img_before_path(reference_img_name)
    output_path = basecls.get_output_path(layout, reference_img_name)
    refresh_cache.main(reference_img_path, output_path, layout)
    # maybe we could test if cache file was created correctly or not

    # And run failed image again but this time the hole should be detected correctly
    ad = AceDistance(
        img_before_path=basecls.get_img_after_path(fails_without_caching_img_name),
        img_after_path=basecls.get_img_after_path(fails_without_caching_img_name),
        out_dir=output_path,
        layout_name=layout,
        debug_mode=False,
        use_cache=True
    )
    ad.run()

    assert ad.pos_hole == pytest.approx([658, 450], abs=15)
