"""Module: Base Parser"""

from abc import ABC, abstractmethod
from typing import Set, Dict


class SwaggerBaseParser(ABC):
    """Class: Swagger Base Parser"""

    def parse_swagger_file(self, file_content: dict, mask: Dict[str, Set[str]]) -> dict:
        """Method: parse swagger file"""

        data = {
            "host": self.parse_host_data(file_content),
            "security": self.parse_security_data(file_content),
            "paths": self.parse_paths_data(file_content, mask),
            "definitions": self.parse_definitions(file_content),
        }
        return data

    @abstractmethod
    def parse_host_data(self, file_content: dict) -> str:
        """Method: parse host data"""
        raise NotImplementedError

    @abstractmethod
    def parse_security_data(self, file_content: dict) -> dict:
        """Method: parse security data"""
        raise NotImplementedError

    @abstractmethod
    def parse_paths_data(self, file_content: dict, mask: Dict[str, Set[str]]) -> dict:
        """Method: parse paths data"""
        raise NotImplementedError

    @abstractmethod
    def parse_definitions(self, file_content: dict) -> dict:
        """Method: parse definitions data"""
        raise NotImplementedError
