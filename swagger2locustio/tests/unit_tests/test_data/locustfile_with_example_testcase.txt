import os
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
