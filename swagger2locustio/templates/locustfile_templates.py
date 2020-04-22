"""Module: Swagger Base Parser"""

from jinja2 import Template


FILE_TEMPLATE = Template("""
import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task

API_PREFIX = ""

{{ required_vars }}

class Tests(TaskSet):

    def on_start(self):
{% if not security_cases %}
        pass
{% else %}
{{ security_cases }}
{% endif %}
{{ test_cases }}

class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)
    {% if host %}
    host = "{{ host }}"
{% endif %}
""")


FUNC_TEMPLATE = Template("""
    @task(1)
    def {{ func_name }}(self):
        self.client.{{ method }}(
            url="{api_prefix}{{ path }}".format(api_prefix=API_PREFIX{{ path_params }}),
            params={{ query_params }},
            headers={{ header_params }},
            cookies={{ cookie_params }}
        )

""")


AUTH_BASIC_TEMPLATE = Template("""
        auth_str = str(os.getenv(\"TEST_USER_LOGIN\")) + ":" + str(os.getenv(\"TEST_USER_PASSWORD\"))
        credentials = b64encode(auth_str.encode()).decode("utf-8")
        credentials = "Basic " + credentials
        self.client.headers.update({"Authorization": credentials})
""")


AUTH_KEY_HEADER_TEMPLATE = Template("""
        self.client.headers.update({"{{ name }}": str(os.getenv(\"TEST_USER_API_KEY\"))})
""")

PATH_PARAM_PAIR_TEMPLATE = Template("{{ key }}={{ val }}")
DICT_PARAM_PAIR_TEMPLATE = Template('"{{ key }}": {{ val }}')
