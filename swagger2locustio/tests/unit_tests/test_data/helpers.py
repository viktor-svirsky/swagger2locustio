import datetime
import random
import string


class Helper:
    @staticmethod
    def get_default_value():
        return None

    @staticmethod
    def get_int_value(start: int = -100, end: int = 100):
        return random.randint(start, end)

    @classmethod
    def get_positive_int_value(start: int = 1, end: int = 100):
        return cls.get_int_value(start, end)

    @classmethod
    def get_negative_int_value(start: int = 1, end: int = 100):
        return cls.get_int_value(start, end)

    @classmethod
    def get_float_value(cls, start: int = -100, end: int = 100):
        return random.random() * cls.get_int_value(start, end)

    @staticmethod
    def get_bool_value():
        return random.choice([True, False])

    @staticmethod
    def get_null_value():
        return None

    @classmethod
    def get_string_value(cls, min_len: int = 0, max_len: int = 100):
        string_len = cls.get_int_value(min_len, max_len)
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=string_len))
