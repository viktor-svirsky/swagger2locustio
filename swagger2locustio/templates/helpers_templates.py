"""Module: locustfile templates"""

from jinja2 import Template

HELPER_MAPPING = {}
HELPER_MAPPING.update(dict.fromkeys(["choice"], "Helper.get_random_choice_from_values(*{values})"))
HELPER_MAPPING.update(dict.fromkeys(["int", "integer", "int32", "int64"], "Helper.get_random_int()"))
HELPER_MAPPING.update(dict.fromkeys(["positiveint", "positive_int"], "Helper.get_random_positive_int()"))
HELPER_MAPPING.update(dict.fromkeys(["negativeint", "negative_int"], "Helper.get_random_negative_int()"))
HELPER_MAPPING.update(dict.fromkeys(["float", "double", "number"], "Helper.get_random_float()"))
HELPER_MAPPING.update(dict.fromkeys(["bool", "boolean"], "Helper.get_random_bool()"))
HELPER_MAPPING.update(dict.fromkeys(["null"], "Helper.get_null_value()"))

HELPER_CLASS = Template(
    """import datetime
import random
import string


class Helper:
    @staticmethod
    def get_random_choice_from_values(*args):
        return random.choice(args)

    @staticmethod
    def get_random_int(start: int = -100, end: int = 100):
        return random.randint(start, end)

    @classmethod
    def get_random_positive_int(cls, start: int = 1, end: int = 100):
        return cls.get_random_int(start, end)

    @classmethod
    def get_random_negative_int(cls, start: int = -100, end: int = -1):
        return cls.get_random_int(start, end)

    @classmethod
    def get_random_float(cls, start: int = -100, end: int = 100):
        return random.random() * cls.get_random_int(start, end)

    @staticmethod
    def get_random_bool():
        return random.choice([True, False])

    @staticmethod
    def get_null_value():
        return None

    @classmethod
    def get_random_string(cls, min_len: int = 0, max_len: int = 100):
        string_len = cls.get_random_int(min_len, max_len)
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=string_len))

    @classmethod
    def get_random_datetime(
        cls,
        result_format: str = "%Y-%m-%d %H:%M:%S",
        min_timestamp: int = 0,
        max_timestamp: int = 1600000000
    ):  # from Unix start time to 09/13/2020 @ 12:26pm (UTC)
        result = cls.get_random_int(min_timestamp, max_timestamp)
        result = datetime.datetime.fromtimestamp(result)
        return result.strftime(result_format)

    @classmethod
    def get_random_password(cls, min_len: int = 8, max_len: int = 25):
        string_len = cls.get_random_int(min_len, max_len)
        return "".join(random.choices(string.ascii_uppercase + string.digits + string.punctuation, k=string_len))

    @classmethod
    def get_random_email(cls, min_len: int = 10, max_len: int = 25):
        username_len = cls.get_random_int(min_len, max_len)
        tld_len = cls.get_random_int(2, 5)
        username_len -= tld_len
        domain_len = cls.get_random_int(5, 10)
        username_len -= domain_len
        if any(i <= 0 for i in [tld_len, domain_len, username_len]):
            return cls.get_random_email()
        tld = "".join(random.choices(string.ascii_lowercase, k=tld_len))
        domain = "".join(random.choices(string.ascii_uppercase + string.digits, k=domain_len))
        username = "".join(random.choices(string.ascii_uppercase + string.digits, k=username_len))
        return f"{ username }@{ domain }.{ tld }"

    @classmethod
    def get_random_ipv4(cls):
        result = cls.get_random_int(0, 255)
        for x in range(3):
            result += "." + cls.get_random_int(0, 255)
        return result

    @classmethod
    def get_random_ipv6(cls):
        result = "".join(random.choices("abcdef" + string.digits, k=4))
        for x in range(7):
            result += ":" + "".join(random.choices("abcdef" + string.digits, k=4))
        return result

"""
)
