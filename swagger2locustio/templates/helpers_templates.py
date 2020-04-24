from jinja2 import Template


HELPER_CLASS_TEMPLATE = Template("""import datetime
import random


class Helper:
    def get_int_value(start: int = -100, end: int = 100):
        return random.randint(start, end)
        
    def get_float_value():
        return random.random()
        
    def get_bool_value():
        return random.choice([True, False])

""")
