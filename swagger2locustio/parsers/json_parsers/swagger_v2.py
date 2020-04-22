"""Module: SwaggerV2 JSON parser"""

from copy import deepcopy
from typing import Set, Dict

from swagger2locustio.parsers.base_parser import SwaggerBaseParser


class SwaggerV2JsonParser(SwaggerBaseParser):
    """Class: SwaggerV2 JSON parser"""

    def _parse_security_data(self, file_content: dict) -> dict:
        security = {}
        security_definitions = file_content.get("securityDefinitions", {})
        for security_type, security_config in security_definitions.items():
            if security_type in ("BasicAuth", "apiKey"):
                security[security_type] = security_config
            else:
                security[security_type] = Ellipsis
        return security

    def _parse_host_data(self, file_content: dict) -> str:
        return file_content.get("host")

    def _parse_paths_data(self, file_content: dict, mask: Dict[str, Set[str]]) -> dict:
        operations_white_list = mask["operations_white_list"]
        paths_white_list = mask["paths_white_list"]
        paths_black_list = mask["paths_black_list"]
        tags_white_list = mask["tags_white_list"]
        tags_black_list = mask["tags_black_list"]

        api_paths = {}
        paths = file_content.get("paths")
        if paths is None:
            raise ValueError("No paths is found in swagger file")
        for path, path_data in paths.items():
            valid_path_methods = {}
            path_name = path.lower()
            if (paths_white_list and path_name not in paths_white_list) or (path_name in paths_black_list):
                continue

            for path_method, method_data in path_data.items():
                if path_method.lower() not in operations_white_list:
                    continue
                tags = set(tag.lower() for tag in method_data.get("tags", []))
                if tags_white_list and not tags_white_list.intersection(tags) or tags_black_list.intersection(tags):
                    continue
                params = method_data.get("parameters", [])
                responses = method_data.get("responses", {})
                param_data = self._parse_params(params)
                method_clean_data = {"params": param_data, "responses": responses}
                valid_path_methods[path_method] = method_clean_data
            api_paths[path] = valid_path_methods
        return api_paths

    def _parse_params(self, params: dict) -> dict:
        param_data = {}
        for param in params:
            param_name = param.get("name")
            # if not param_name or not param.get("default") or not param.get("in"):
            if not param_name or not param.get("in"):
                if param.get("required"):
                    raise ValueError("Not full info about required param")
                continue
            param_data[param_name] = deepcopy(param)
        return param_data

    def _parse_definitions(self, file_content: dict) -> dict:
        return {}
