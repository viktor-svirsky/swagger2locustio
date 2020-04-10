from abc import ABC, abstractmethod
from typing import Set, Dict


class SwaggerBaseParser(ABC):
    def parse_swagger_file(self, file_content: dict, mask: Dict[str, Set[str]]) -> dict:
        data = {
            "security": self._parse_security_data(file_content),
            "paths": self._parse_paths_data(file_content, mask),
            "definitions": self._parse_definitions(file_content)
        }
        return data

    @abstractmethod
    def _parse_security_data(self, file_content: dict) -> dict:
        pass

    @abstractmethod
    def _parse_paths_data(self, file_content: dict, mask: Dict[str, Set[str]]) -> dict:
        pass

    @abstractmethod
    def _parse_definitions(self, file_content: dict) -> dict:
        pass
