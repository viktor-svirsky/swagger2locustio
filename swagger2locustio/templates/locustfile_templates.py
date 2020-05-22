"""Module: locustfile templates"""

from jinja2 import Template

MAIN_LOCUSTFILE = Template(
    """from locust import HttpLocust

from apps.{{ app_name }}.generated_taskset import GeneratedTaskSet


class TestUser(HttpLocust):
    task_set = GeneratedTaskSet
    min_wait = 5 * 1000
    max_wait = 10 * 1000
    host = "{{ host }}"

"""
)

BASE_TASKSET_FILE = Template(
    """import os
from base64 import b64encode
from locust import TaskSet as LocustTaskSet

from constants.base_constants import API_PREFIX
from apps.helper import Helper


class TaskSet(LocustTaskSet):

    def on_start(self):
        self.login()

    def on_stop(self):
        pass

    def login(self):{% if not security_cases %}
        pass{% else %}{{ security_cases }}{% endif %}

    def url(self, _url: str, **kwargs):
        return API_PREFIX + _url.format(**kwargs)

    def get_generic_name(self, file):
        if os.environ.get("DEBUG"):
            return None
        return (
            "-".join(os.path.realpath(file).split("/")[-3:])
            .replace("_", "-")
            .replace(".py", "")
        )

"""
)

GENERATED_TASKSET_FILE = Template(
    """from apps.base import TaskSet
from apps.helper import Helper
{% for class_import in test_classes_imports %}{{ class_import }}
{% endfor %}

class GeneratedTaskSet(
    {% for test_class in test_classes_names %}{{ test_class }},
    {% endfor %}TaskSet
):
    pass

"""
)

TEST_CLASS_FILE = Template(
    """from locust import task

from apps.base import TaskSet
from apps.helper import Helper
{% if constants %}from apps.{{ app_name }}.constants.{{ file_name }} import {{ constants }}{% endif %}


class {{ class_name }}(TaskSet):
{{ test_methods }}
"""
)


FUNC = Template(
    """
    @task(1)
    def {{ func_name }}(self):
        self.client.{{ method }}(
            name=self.get_generic_name(__file__),
            url=self.url("{{ path }}"{{ path_params }}),
            params={{ query_params }},
            headers={{ header_params }},
            cookies={{ cookie_params }},
        )

"""
)

PATH_PARAM_PAIR = Template("{{ key }}={{ val }}")
DICT_PARAM_PAIR = Template('"{{ key }}": {{ val }}')
