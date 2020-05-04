"""Module: locustfile templates"""

from jinja2 import Template


FILE_TEMPLATE = Template(
    """import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task

from helpers import Helper

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
"""
)


FUNC_TEMPLATE = Template(
    """
    @task(1)
    def {{ func_name }}(self):
        self.client.{{ method }}(
            url="{api_prefix}{{ path }}".format(api_prefix=API_PREFIX{{ path_params }}),
            params={{ query_params }},
            headers={{ header_params }},
            cookies={{ cookie_params }},
        )

"""
)

PATH_PARAM_PAIR_TEMPLATE = Template("{{ key }}={{ val }}")
DICT_PARAM_PAIR_TEMPLATE = Template('"{{ key }}": {{ val }}')
