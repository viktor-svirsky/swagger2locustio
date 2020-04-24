import logging
from itertools import combinations
from copy import deepcopy
from typing import List, Dict, Union

from swagger2locustio.templates import locustfile_templates as l_templates

log = logging.getLogger(__name__)


class BaseGenerator:
    def __init__(self, strict_level: int):
        self.strict_level = strict_level
        self.vars_without_values: Dict[str, dict] = {}

    def generate_locustfile(self, swagger_data: dict) -> str:
        test_cases = self.generate_test_cases(swagger_data["paths"])
        security_data = swagger_data["security"]
        security_cases = ""
        if security_data:
            security_cases = self.generate_security_cases(security_data)
        code = self.generate_code_from_template(test_cases, security_cases, swagger_data["host"])
        return code

    def generate_test_cases(self, paths_data: dict) -> str:
        funcs = []
        test_count = 0
        for path, methods_data in paths_data.items():
            for method, method_data in methods_data.items():
                params_data = method_data.get("params", {})
                # responses_data = method_data.get("responses", {})
                case = 0
                try:
                    params_combinations = self.generate_params(params_data)
                except ValueError as e:
                    logging.warning(e)
                    continue

                for path_parameters in params_combinations["path_params"]:
                    for query_parameters in params_combinations["query_params"]:
                        for header_parameters in params_combinations["header_params"]:
                            for cookie_parameters in params_combinations["cookie_params"]:
                                func_name = f"test_{test_count}_case_{case}"
                                func = l_templates.func_template.render(
                                    func_name=func_name,
                                    method=method,
                                    path=path,
                                    path_params=self._format_params(path_parameters, test_count, "path"),
                                    query_params=self._format_params(query_parameters, test_count, "query"),
                                    header_params=self._format_params(header_parameters, test_count, "header"),
                                    cookie_params=self._format_params(cookie_parameters, test_count, "cookie")
                                )
                                funcs.append(func)
                                case += 1
                test_count += 1
        return "".join(funcs)

    def generate_params(self, params: dict) -> Dict[str, List[List[dict]]]:
        extracted_params = self._extract_params(params)
        return {
            key: self._create_params_combinations(extracted_params[key]) for key in
            ["path_params", "query_params", "header_params", "cookie_params"]
        }

    def _format_params(self, raw_params: List[dict], test_count: int, param_type) -> Union[str, dict]:
        params = []
        for param in raw_params:
            name = param.get("name")
            val = param.get("default")
            if not val:
                val = f"{name}_test_{test_count}"
                self.vars_without_values[val] = param
            else:
                val = repr(val)
            if param_type == "path":
                params.append(l_templates.path_param_pair_template.render(key=name, val=val))
            else:
                params.append(l_templates.dict_param_pair_template.render(key=name, val=val))
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
        path_params: Dict[str, list] = {
            "required": [],
            "not_required": []
        }
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

    def _create_params_combinations(self, params: Dict[str, list]) -> List[List[Dict]]:
        not_required_query_params = params["not_required"]
        required_query_params = params["required"]
        params_combinations = []
        for combination_count in range(len(not_required_query_params) + 1):
            for not_required_combination in combinations(not_required_query_params, combination_count):
                combination = required_query_params.copy()
                combination += list(not_required_combination)
                params_combinations.append(combination)
        return params_combinations

    def generate_security_cases(self, security_data: dict) -> str:
        security_cases = []
        for security_type, security_config in security_data.items():
            if security_type == "BasicAuth":
                security_cases.append(l_templates.auth_basic_template.render())
            elif security_type == "apiKey":
                location = security_config.get("in")
                name = security_config.get("name")
                if location.lower() == "header" and name:
                    security_cases.append(l_templates.auth_key_header_template.render(name=name))
                else:
                    raise ValueError(security_config)
        return "".join(security_cases)

    def generate_code_from_template(self, test_cases: str, security_cases: str, host: str) -> str:
        required_vars = []
        for var, var_data in self.vars_without_values.items():
            required_vars.append(f"{var} = \"#\"  # {var_data}")
        vars_str = "\n".join(required_vars)
        return l_templates.file_template.render(
            required_vars=vars_str,
            test_cases=test_cases,
            security_cases=security_cases,
            host=host
        )
