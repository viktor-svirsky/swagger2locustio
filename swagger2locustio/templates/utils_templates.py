"""Module: utils templates"""

from jinja2 import Template

HELPER_CLASS_TEMPLATE = Template(
    """
def get_generic_name(file):
    return (
        "-".join(os.path.realpath(file).split("/")[-3:])
        .replace("_", "-")
        .replace(".py", "")
    )
"""
)