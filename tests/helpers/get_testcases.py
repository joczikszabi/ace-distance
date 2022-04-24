import os
import json


def get_testcases(test_data_path):
    testcases_json = os.path.join(test_data_path, 'test_cases.json')

    if not os.path.isfile(testcases_json):
        return None

    with open(testcases_json, 'r') as f:
        data = json.load(f)

    return data['test_cases']
