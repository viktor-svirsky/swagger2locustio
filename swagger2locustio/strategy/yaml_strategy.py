"""Module: YAML Strategy"""

import yaml

from swagger2locustio.strategy.base_strategy import BaseStrategy
from swagger2locustio.parsers.base_parser import SwaggerBaseParser
from swagger2locustio.parsers.yaml_parsers.swagger_v2 import SwaggerV2YamlParser


class YamlStrategy(BaseStrategy):
    """Class: YAML Strategy"""

    @staticmethod
    def read_file_content(file_name: str) -> dict:
        with open(file_name) as file:
            return yaml.safe_load(file)

    def get_specific_version_parser(self) -> SwaggerBaseParser:
        parser = SwaggerV2YamlParser()

        return self.get_specific_version_parser_basic(parser)
