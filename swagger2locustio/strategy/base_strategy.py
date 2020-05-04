"""Module: Base Strategy"""

from abc import abstractmethod, ABC
from pathlib import Path
from typing import Set, Dict

from swagger2locustio.parsers.base_parser import SwaggerBaseParser
from swagger2locustio.generators.base_generator import BaseGenerator


class BaseStrategy(ABC):
    """Class: Base Strategy"""

    def __init__(self, file_name: Path, results_path: Path, mask: Dict[str, Set[str]], strict_level: int, max_folder_depth: int):
        self.swagger_file_content = self.read_file_content(str(file_name))
        self.mask = mask
        self.generator = BaseGenerator(results_path, strict_level, max_folder_depth)
        results_path.mkdir(exist_ok=True)

    @staticmethod
    @abstractmethod
    def read_file_content(file_name: str) -> dict:
        """Method: read file content"""

        raise NotImplementedError

    @abstractmethod
    def get_specific_version_parser(self) -> SwaggerBaseParser:
        """Method: get specific version parser"""

        raise NotImplementedError

    def process(self):
        """Method: process"""

        specific_version_parser = self.get_specific_version_parser()
        swagger_data = specific_version_parser.parse_swagger_file(self.swagger_file_content, self.mask)
        self.generator.generate_locustfiles(swagger_data)
