"""Module: locustfile templates"""

from jinja2 import Template

MAIN_LOCUSTFILE = Template(
    """import os
from base64 import b64encode
from locust import HttpLocust, between

from helpers import Helper
from testsets.generated_testset import GeneratedTestSet


class Tests(GeneratedTestSet):

    def on_start(self):{% if not security_cases %}
        pass{% else %}{{ security_cases }}{% endif %}

    def on_stop(self):
        pass


class TestUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)
    host = "{{ host }}"

"""
)

GENERATED_TESTSET_FILE = Template(
    """from locust import TaskSet

from helpers import Helper
from constants.base_constants import API_PREFIX
{% for class_import in test_classes_imports %}{{ class_import }}
{% endfor %}

class GeneratedTestSet(TaskSet{% for test_class in test_classes_names %}, {{ test_class }}{% endfor %}):
    pass

"""
)

TEST_CLASS_FILE = Template(
    """from locust import TaskSet, task

from helpers import Helper
from constants.base_constants import API_PREFIX
{% if constants %}from constants.{{ file_name }} import {{ constants }}{% endif %}


class {{ class_name }}(TaskSet):
{{ test_methods }}
"""
)


FUNC = Template(
    """
    @task(1)
    def {{ func_name }}(self):
        self.client.{{ method }}(
            name="{{ test_name }}",
            url="{api_prefix}{{ path }}".format(api_prefix=API_PREFIX{{ path_params }}),
            params={{ query_params }},
            headers={{ header_params }},
            cookies={{ cookie_params }},
        )

"""
)

PATH_PARAM_PAIR = Template("{{ key }}={{ val }}")
DICT_PARAM_PAIR = Template('"{{ key }}": {{ val }}')
