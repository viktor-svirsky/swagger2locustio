from abc import abstractmethod, ABC
from pathlib import Path
from typing import Set, Dict

from swagger2locustio.parsers.base_parser import SwaggerBaseParser
from swagger2locustio.generators.base_generator import BaseGenerator


class BaseStrategy(ABC):
    def __init__(self, file_name: Path, results_path: Path, mask: Dict[str, Set[str]], strict_level: int):
        self.swagger_file_content = self.read_file_content(str(file_name))
        self.mask = mask
        self.generator = BaseGenerator(strict_level)
        results_path.mkdir(exist_ok=True)
        self.results_file = str(results_path / "locustfile.py")

    @staticmethod
    @abstractmethod
    def read_file_content(file_name: str) -> dict:
        pass

    @abstractmethod
    def get_specific_version_parser(self) -> SwaggerBaseParser:
        pass

    def process(self):
        specific_version_parser = self.get_specific_version_parser()
        swagger_data = specific_version_parser.parse_swagger_file(
            self.swagger_file_content,
            self.mask
        )
        code = self.generator.generate_locustfile(swagger_data)
        self.write_results_to_file(code)

    def write_results_to_file(self, content: str):
        with open(self.results_file, "w") as f:
            f.write(content)
