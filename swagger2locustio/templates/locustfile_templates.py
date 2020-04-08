file_template = """
import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task


class Tests(TaskSet):

    def on_start(self):
        pass
{security_cases}
{test_cases}

class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)
"""


func_template = """
    @task(1)
    def {func_name}(self):
        self.client.{method}(url="{path}"{path_params}, params={query_params}, headers={header_params}, cookies={cookie_params})
"""


auth_basic_template = """
        auth_str = str(os.getenv(\"TEST_USER_LOGIN\")) + ":" + str(os.getenv(\"TEST_USER_PASSWORD\"))
        credentials = b64encode(auth_str.encode()).decode("utf-8")
        credentials = "Basic " + credentials
        self.client.headers.update(dict(Authorization=credentials))
"""


auth_key_header_template = """
        self.client.headers.update(dict({name}=str(os.getenv(\"TEST_USER_API_KEY\"))))
"""
