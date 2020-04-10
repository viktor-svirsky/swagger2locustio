import logging
from itertools import combinations
from copy import copy, deepcopy
from typing import List, Dict

from swagger2locustio.templates import locustfile_templates as l_templates

log = logging.getLogger(__name__)


class BaseGenerator:
    def __init__(self, strict: bool):
        self.strict = strict
        self.vars_without_values = set()

    def generate_code(self, swagger_data: dict) -> str:
        test_cases = self.generate_test_cases(swagger_data["paths"])
        security_data = swagger_data["security"]
        security_cases = None
        if security_data:
            security_cases = self.generate_security_cases(security_data)
        code = self.generate_code_from_template(test_cases, security_cases)
        return code

    def generate_test_cases(self, paths_data: dict) -> str:
        funcs = []
        test_count = 0
        for path, methods_data in paths_data.items():
            for method, method_data in methods_data.items():
                params_data = method_data.get("params", {})
                responses_data = method_data.get("responses", {})
                case = 0
                try:
                    params_combinations = self.generate_params(params_data)
                except ValueError as e:
                    logging.info(e)
                    continue
                for path_parameters in params_combinations["path_params"]:
                    for query_parameters in params_combinations["query_params"]:
                        for header_parameters in params_combinations["header_params"]:
                            for cookie_parameters in params_combinations["cookie_params"]:
                                func_name = f"test_{test_count}_case_{case}"
                                path_parameters_str = ""
                                if path_parameters:
                                    parameters_pairs = []
                                    for key, val in path_parameters.items():
                                        if val == Ellipsis:
                                            val = f"{key}_test_{test_count}"
                                            self.vars_without_values.add(val)
                                        else:
                                            val = repr(val)
                                        pair = l_templates.path_param_pair_template.render(key=key, val=val)
                                        parameters_pairs.append(pair)
                                    path_parameters_str = ", ".join(parameters_pairs)
                                path_par = f".format({path_parameters_str})"
                                func = l_templates.func_template.render(
                                    func_name=func_name,
                                    method=method,
                                    path=path,
                                    path_params=path_par,
                                    query_params=query_parameters,
                                    header_params=header_parameters,
                                    cookie_params=cookie_parameters
                                )
                                funcs.append(func)
                                case += 1
                test_count += 1
        return "".join(funcs)

    def generate_params(self, params: dict) -> Dict[str, List[dict]]:
        path_params = {
            "required": [],
            "not_required": []
        }
        query_params = deepcopy(path_params)
        header_params = deepcopy(path_params)
        cookie_params = deepcopy(path_params)
        for param, param_config in params.items():
            param_location = param_config.get("in")
            required = param_config.get("required")
            default_val = param_config.get("default")
            target_params = ...
            if param_location == "query":
                target_params = query_params
            elif param_location == "path":
                target_params = path_params
            elif param_location == "header":
                target_params = header_params
            elif param_location == "cookie":
                target_params = cookie_params
            else:
                raise ValueError(f"Not valid {param} `in` value: {param_location}")

            if not required and default_val is not None:
                target_params["not_required"].append({param: default_val})
            elif required:
                if default_val is not None:
                    target_params["required"].append({param: default_val})
                elif not self.strict:
                    target_params["required"].append({param: ...})
                else:
                    raise ValueError(f"No default value found for required {param_location} param {param}")
        params_combinations = {
            "path_params": self.make_params_combinations(path_params),
            "query_params": self.make_params_combinations(query_params),
            "header_params": self.make_params_combinations(header_params),
            "cookie_params": self.make_params_combinations(cookie_params),
        }
        return params_combinations

    def make_params_combinations(self, params: dict) -> List[dict]:
        not_required_query_params = params["not_required"]
        required_query_params = {}
        params_list = []
        for sub_dict in params["required"]:
            required_query_params.update(sub_dict)
        for param_count in range(len(not_required_query_params) + 1):
            for params in combinations(not_required_query_params, param_count):
                query_params = copy(required_query_params)
                for sub_dict in params:
                    query_params.update(sub_dict)
                params_list.append(query_params)
        return params_list

    def generate_security_cases(self, security_data: dict) -> str:
        security_cases = []
        for security_type, security_config in security_data.items():
            if security_type == "BasicAuth":
                security_cases.append(l_templates.auth_basic_template)
            elif security_type == "apiKey":
                location = security_config.get("in")
                name = security_config.get("name")
                if location.lower() == "header" and name:
                    security_cases.append(l_templates.auth_key_header_template.render(name=name))
                else:
                    raise ValueError(security_config)
        return "".join(security_cases)

    def generate_code_from_template(self, test_cases: str, security_cases: str) -> str:
        vars_str = "\n".join(f"{var} = " for var in self.vars_without_values)
        return l_templates.file_template.render(
            required_vars=vars_str,
            test_cases=test_cases,
            security_cases=security_cases
        )
