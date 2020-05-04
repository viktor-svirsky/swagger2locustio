"""Module: Base Generator"""

import logging
from itertools import combinations
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Union
from pprint import pprint

from swagger2locustio.templates import locustfile_templates
from swagger2locustio.templates import helpers_templates
from swagger2locustio.templates import auth_templates

LOG = logging.getLogger(__name__)


class BaseGenerator:
    """Class: Base Generator"""

    def __init__(self, results_path: Path, strict_level: int, max_folder_depth: int):
        self.strict_level = strict_level
        self.results_path = results_path
        self.max_folder_depth = max_folder_depth

    def generate_locustfiles(self, swagger_data: dict) -> None:
        """Method: generate locustfiles structure"""

        test_cases = self.generate_test_cases(swagger_data["paths"])
        security_data = swagger_data["security"]
        security_cases = ""
        if security_data:
            security_cases = self.generate_security_cases(security_data)
        code = self.generate_code_from_template(test_cases, security_cases, swagger_data["host"])
        helpers = self.generate_helpers_from_template()
        (self.results_path / "locustfile.py").write_text(code)
        (self.results_path / "helpers.py").write_text(helpers)

    def generate_test_cases(self, paths_data: dict) -> str:
        """Method: generate test cases"""
        funcs = []
        test_count = 0
        for path, methods_data in paths_data.items():
            for method, method_data in methods_data.items():
                # responses_data = method_data.get("responses", {})
                try:
                    params = self.generate_params(method_data.get("params", {}))
                except ValueError as error:
                    logging.warning(error)
                    continue
                pprint(f"test_{test_count}")
                pprint(params)
                funcs.append(
                    locustfile_templates.FUNC_TEMPLATE.render(
                        func_name=f"test_{test_count}",
                        method=method,
                        path=path,
                        path_params=self._format_params(params["path_params"], "path"),
                        query_params=self._format_params(params["query_params"], "query"),
                        header_params=self._format_params(params["header_params"], "header"),
                        cookie_params=self._format_params(params["cookie_params"], "cookie"),
                    )
                )
                test_count += 1
        return "".join(funcs)

    def generate_params(self, params: dict) -> Dict[str, list]:
        """Method: generate params"""

        extracted_params = self._extract_params(params)
        clean_params = {}
        for param_type in extracted_params:
            clean_params[param_type] = extracted_params[param_type]["required"] + extracted_params[param_type]["not_required"]
        return clean_params

    @staticmethod
    def _format_params(raw_params: List[dict], param_type) -> Union[str, dict]:
        print(raw_params)
        params = []
        for param in raw_params:
            name = param.get("name")
            val = param.get("default")
            if val is None:
                param_value_type = param.get("type")
                val = helpers_templates.HELPER_MAPPING[param_value_type] + "()"
            else:
                val = repr(val)
            if param_type == "path":
                params.append(locustfile_templates.PATH_PARAM_PAIR_TEMPLATE.render(key=name, val=val))
            else:
                params.append(locustfile_templates.DICT_PARAM_PAIR_TEMPLATE.render(key=name, val=val))
        formatted_params = ""
        if param_type == "path":
            if params:
                formatted_params = ", " + ", ".join(params)
        else:
            if not params:
                formatted_params = "{}"
            else:
                formatted_params = "{" + ", ".join(params) + "}"
        return formatted_params

    def _extract_params(self, params: dict) -> Dict[str, Dict[str, list]]:
        path_params: Dict[str, list] = {"required": [], "not_required": []}
        query_params = deepcopy(path_params)
        header_params = deepcopy(path_params)
        cookie_params = deepcopy(path_params)
        for param, param_config in params.items():
            param_location = param_config.get("in")
            required = param_config.get("required")
            required_type = "required" if required else "not_required"
            default_val = param_config.get("default")
            if param_location == "query":
                target_params = query_params
            elif param_location == "path":
                target_params = path_params
            elif param_location == "header":
                target_params = header_params
            elif param_location == "cookie":
                target_params = cookie_params
            else:
                raise ValueError(f"Not valid {param} `in` value: {param_location}", param_config)

            if self.strict_level == 0:
                target_params[required_type].append(param_config)
            elif self.strict_level == 1 and (default_val or (not default_val and required)):
                target_params[required_type].append(param_config)
            elif self.strict_level == 2:
                if default_val:
                    target_params[required_type].append(param_config)
                else:
                    raise ValueError(f"No default value found for required {param_location} param {param}")
        params = {
            "path_params": path_params,
            "query_params": query_params,
            "header_params": header_params,
            "cookie_params": cookie_params,
        }
        return params

    @staticmethod
    def generate_security_cases(security_data: dict) -> str:
        """Method: generate security cases"""

        security_cases = []
        for security_type, security_config in security_data.items():
            if security_type == "BasicAuth":
                security_cases.append(auth_templates.AUTH_BASIC_TEMPLATE.render())
            elif security_type == "apiKey":
                location = security_config.get("in")
                name = security_config.get("name")
                if location.lower() == "header" and name:
                    security_cases.append(auth_templates.AUTH_KEY_HEADER_TEMPLATE.render(name=name))
                else:
                    raise ValueError(security_config)
        return "".join(security_cases)

    @staticmethod
    def generate_code_from_template(test_cases: str, security_cases: str, host: str) -> str:
        """Method: generate code from template"""

        required_vars = []
        vars_str = "\n".join(required_vars)
        return locustfile_templates.FILE_TEMPLATE.render(
            required_vars=vars_str, test_cases=test_cases, security_cases=security_cases, host=host
        )

    @staticmethod
    def generate_helpers_from_template() -> str:
        return helpers_templates.HELPER_CLASS_TEMPLATE.render()
