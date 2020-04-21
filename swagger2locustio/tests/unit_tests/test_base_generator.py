import unittest

from swagger2locustio.generators.base_generator import BaseGenerator


#TODO Should be adjusted
class TestBaseGenerator(unittest.TestCase):

    def test_empty_swagger_file(self):
        swagger_data = {
            "host": dict(),
            "security": dict(),
            "paths": dict(),
            "definitions": dict()
        }
        ref_locust_file = ("""
import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task\n
API_PREFIX = ""\n\n\n
class Tests(TaskSet):\n
    def on_start(self):\n
        pass\n\n\n
class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)
    """)
        locust_file = BaseGenerator(strict_level=0).generate_locustfile(swagger_data=swagger_data)
        self.assertEqual(locust_file, ref_locust_file)

        locust_file = BaseGenerator(strict_level=1).generate_locustfile(swagger_data=swagger_data)
        self.assertEqual(locust_file, ref_locust_file)

        locust_file = BaseGenerator(strict_level=2).generate_locustfile(swagger_data=swagger_data)
        self.assertEqual(locust_file, ref_locust_file)

    def test_empty_fields_selectively(self):
        swagger_data = {
            "host": 'api.example.com',
            "security": dict(),
            "paths": {'/example': {'get': {'params': {'example': {'name': 'example', 'in': 'query'}}}}},
            "definitions": dict()
        }
        ref_locust_file = ("""
import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task\n
API_PREFIX = ""\n\n\n
class Tests(TaskSet):\n
    def on_start(self):\n
        pass\n\n
    @task(1)
    def test_0_case_0(self):
        self.client.get(
            url="{api_prefix}/example".format(api_prefix=API_PREFIX),
            params={},
            headers={},
            cookies={}
        )\n\n
class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)\n    
    host = \"api.example.com\"
""")

        locust_file = BaseGenerator(strict_level=0).generate_locustfile(swagger_data=swagger_data)
        self.assertEqual(locust_file, ref_locust_file)


# TODO 1. to fill up test cases with not emtpy swagger file except of one of the keys.
# TODO 2. create a few test cases with correct swagger files

if __name__ == "__main__":
    unittest.main()