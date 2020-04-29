import unittest
from pathlib import Path
import os

from swagger2locustio.strategy.json_strategy import JsonStrategy


class TestStrategyJSON(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName=methodName)
        self.swagger_file = "swagger_file.json"
        self.generated_file = "swagger2locustio/tests/unit_tests/test_data/locustfile.py"
        self.LOCUSTFILE_WITH_EXAMPLE_TESTCASE = """import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task

API_PREFIX = ""

param1_test_0 = "#"  # {'name': 'param1', 'in': 'query', 'description': 'description', 'required': True, 'type': 'number', 'format': 'double'}
param2_test_0 = "#"  # {'name': 'param2', 'in': 'query', 'description': 'description', 'required': True, 'type': 'number', 'format': 'double'}

class Tests(TaskSet):

    def on_start(self):

        pass


    @task(1)
    def test_0_case_0(self):
        self.client.get(
            url="{api_prefix}/example".format(api_prefix=API_PREFIX),
            params={"param1": param1_test_0, "param2": param2_test_0},
            headers={},
            cookies={},
        )


class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)

    host = "api.example.com"
"""
        self.LOCUSTFILE_WITHOUT_TESTCASES = """import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task

API_PREFIX = ""



class Tests(TaskSet):

    def on_start(self):

        pass



class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)

    host = "api.example.com"
"""

    def tearDown(self) -> None:
        if os.path.exists(self.generated_file):
            os.remove(self.generated_file)

    def _check_result(self, mask, locust_example, strict=False):
        json_str = JsonStrategy(
            file_name=Path("swagger2locustio/tests/unit_tests/test_data/" + self.swagger_file),
            results_path=Path("swagger2locustio/tests/unit_tests/test_data/"),
            mask=mask,
            strict=strict,
        )
        json_str.process()
        exists = os.path.exists(self.generated_file)
        self.assertTrue(exists)
        if exists:
            with open(self.generated_file, "r") as file:
                self.assertEqual(file.read(), locust_example)

    def test_process_interface(self):
        mask = {
            "operations_white_list": {"get"},
            "paths_white_list": set(),
            "paths_black_list": set(),
            "tags_white_list": set(),
            "tags_black_list": set(),
        }
        self._check_result(mask, self.LOCUSTFILE_WITH_EXAMPLE_TESTCASE)

    def test_process_interface_with_paths_black_list(self):
        mask = {
            "operations_white_list": {"get"},
            "paths_white_list": set(),
            "paths_black_list": {"/example"},
            "tags_white_list": set(),
            "tags_black_list": set(),
        }
        self._check_result(mask, self.LOCUSTFILE_WITHOUT_TESTCASES)

    def test_process_interface_with_paths_white_list(self):
        mask = {
            "operations_white_list": {"get"},
            "paths_white_list": {"/example"},
            "paths_black_list": set(),
            "tags_white_list": set(),
            "tags_black_list": set(),
        }
        self._check_result(mask, self.LOCUSTFILE_WITH_EXAMPLE_TESTCASE)

    def test_process_interface_without_operations_list(self):
        mask = {
            "operations_white_list": set(),
            "paths_white_list": set(),
            "paths_black_list": set(),
            "tags_white_list": set(),
            "tags_black_list": set(),
        }
        self._check_result(mask, self.LOCUSTFILE_WITHOUT_TESTCASES)

    def test_process_interface_with_tags_white_list(self):
        mask = {
            "operations_white_list": {"get"},
            "paths_white_list": set(),
            "paths_black_list": set(),
            "tags_white_list": {"example"},
            "tags_black_list": set(),
        }
        self._check_result(mask, self.LOCUSTFILE_WITH_EXAMPLE_TESTCASE)

    def test_process_interface_with_tags_black_list(self):
        mask = {
            "operations_white_list": {"get"},
            "paths_white_list": set(),
            "paths_black_list": set(),
            "tags_white_list": set(),
            "tags_black_list": {"example"},
        }
        self._check_result(mask, self.LOCUSTFILE_WITHOUT_TESTCASES)


if __name__ == "__main__":
    unittest.main()
