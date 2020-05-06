"""Module: Auth templates"""

from jinja2 import Template

AUTH_BASIC_TEMPLATE = Template(
    """
        auth_str = str(os.getenv(\"TEST_USER_LOGIN\")) + ":" + str(os.getenv(\"TEST_USER_PASSWORD\"))
        credentials = b64encode(auth_str.encode()).decode("utf-8")
        credentials = "Basic " + credentials
        self.client.headers.update({"Authorization": credentials})
        
"""
)


AUTH_KEY_HEADER_TEMPLATE = Template(
    """
        self.client.headers.update({"{{ name }}": str(os.getenv(\"TEST_USER_API_KEY\"))})
        
"""
)
