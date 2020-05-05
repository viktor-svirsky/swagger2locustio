"""Module: constants templates"""

from jinja2 import Template

CONSTANTS_BASE_FILE_TEMPLATE = Template(
    """from helpers import Helper

API_PREFIX = ""

"""
)

CONSTANTS_FILE_TEMPLATE = Template(
    """from helpers import Helper

{% for const in constants %}# value type -> {{ const.value_type }}
{{ const.name }} = [{{ const.val }}]
{% endfor %}
"""
)
