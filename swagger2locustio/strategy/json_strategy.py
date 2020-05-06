"""Module: JSON Strategy"""

import json

from swagger2locustio.strategy.base_strategy import BaseStrategy
from swagger2locustio.parsers.base_parser import SwaggerBaseParser
from swagger2locustio.parsers.json_parsers.swagger_v2 import SwaggerV2JsonParser


class JsonStrategy(BaseStrategy):
    """Class: JSON Strategy"""

    @staticmethod
    def read_file_content(file_name: str) -> dict:
        with open(file_name) as file:
            return json.load(file)

    def get_specific_version_parser(self) -> SwaggerBaseParser:
        parser = SwaggerV2JsonParser()

        return self.get_specific_version_parser_basic(parser)
