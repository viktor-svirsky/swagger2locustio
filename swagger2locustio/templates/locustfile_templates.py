"""Module: locustfile templates"""

from jinja2 import Template

MAIN_LOCUSTFILE = Template(
    """from locust import HttpLocust, between

from tasksets.generated_taskset import GeneratedTaskSet


class TestUser(HttpLocust):
    task_set = GeneratedTaskSet
    wait_time = between(5.0, 9.0)
    host = "{{ host }}"

"""
)

BASE_TASKSET_FILE = Template(
    """import os
from base64 import b64encode
from locust import TaskSet as LocustTaskSet

from tasksets.helper import Helper


class TaskSet(LocustTaskSet):

    def on_start(self):
        self.login()

    def on_stop(self):
        pass

    def login(self):{% if not security_cases %}
        pass{% else %}{{ security_cases }}{% endif %}

    def url(self, _url: str, **kwargs):
        return _url.format(**kwargs)

    def get_generic_name(self, file):
        return (
            "-".join(os.path.realpath(file).split("/")[-3:])
            .replace("_", "-")
            .replace(".py", "")
        )

"""
)

GENERATED_TASKSET_FILE = Template(
    """from tasksets.base import TaskSet
from tasksets.helper import Helper
from constants.base_constants import API_PREFIX
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

from tasksets.base import TaskSet
from tasksets.helper import Helper
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
            name=self.get_generic_name(__file__),
            url=self.url("{api_prefix}{{ path }}".format(api_prefix=API_PREFIX{{ path_params }})),
            params={{ query_params }},
            headers={{ header_params }},
            cookies={{ cookie_params }},
        )

"""
)

PATH_PARAM_PAIR = Template("{{ key }}={{ val }}")
DICT_PARAM_PAIR = Template('"{{ key }}": {{ val }}')
