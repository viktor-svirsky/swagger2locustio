"""Module: SwaggerV3 parser"""

from swagger2locustio.parsers.base_parser import SwaggerBaseParser


class SwaggerV3Parser(SwaggerBaseParser):
    """Class: SwaggerV3 parser"""

    @staticmethod
    def _parse_params(params: dict) -> dict:
        raise NotImplementedError()
