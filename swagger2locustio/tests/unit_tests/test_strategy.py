import unittest
from pathlib import Path
import os

from swagger2locustio.strategy.json_strategy import JsonStrategy


class TestStrategyJSON(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName=methodName)
        self.swagger_file = "swagger_file.json"
        self.generated_file = "swagger2locustio/tests/unit_tests/test_data/locustfile.py"
        with open("swagger2locustio/tests/unit_tests/test_data/locustfile_with_example_testcase.txt", "r") as file:
            self.LOCUSTFILE_WITH_EXAMPLE_TESTCASE = file.read()
        with open("swagger2locustio/tests/unit_tests/test_data/locustfile_without_testcases.txt", "r") as file:
            self.LOCUSTFILE_WITHOUT_TESTCASES = file.read()

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
