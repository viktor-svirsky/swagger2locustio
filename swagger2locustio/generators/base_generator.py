"""Module: Base Generator"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Union, Any

from swagger2locustio.templates import locustfile_templates
from swagger2locustio.templates import helpers_templates
from swagger2locustio.templates import auth_templates
from swagger2locustio.templates import constants_templates

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class Constant:
    name: str
    val: Any
    value_type: str


@dataclass
class TestMethod:
    method_data: str
    constants: List[Constant] = field(default_factory=lambda: [])


@dataclass
class TestClass:
    file_path: Path
    file_name: str
    class_name: str
    test_methods: List[TestMethod] = field(default_factory=lambda: [])


class BaseGenerator:
    """Class: Base Generator"""

    def __init__(self, results_path: Path, strict_level: int, max_folder_depth: int):
        self.results_path = results_path
        self.max_folder_depth = max_folder_depth
        self.constants_path = self.results_path / "constants"
        self.constants_path.mkdir(exist_ok=True, parents=True)
        self.tests_path = self.results_path / "tests"
        self.tests_path.mkdir(exist_ok=True, parents=True)

    def generate_locustfiles(self, swagger_data: dict) -> None:
        """Method: generate locustfiles structure"""

        test_classes = self.generate_test_classes(swagger_data["paths"])
        security_data = swagger_data["security"]
        security_cases = ""
        if security_data:
            security_cases = self.generate_security_cases(security_data)
        test_classes_imports = []
        for test_class in test_classes.values():
            test_methods = []
            class_constants = set()
            for test_method in test_class.test_methods:
                test_methods.append(test_method.method_data)
                class_constants.update(test_method.constants)
            test_methods_str = "".join(test_methods)
            test_class_path = self.tests_path / test_class.file_path
            test_class_path.mkdir(parents=True, exist_ok=True)
            file_name = f"{test_class.file_name}.py"
            constants_str = ", ".join([constant.name for constant in class_constants])
            import_path = str("tests" / test_class.file_path / test_class.file_name).replace("/", ".")
            test_classes_imports.append(f"from {import_path} import {test_class.class_name}")
            (test_class_path / file_name).write_text(
                locustfile_templates.FILE_TEMPLATE.render(
                    file_name=test_class.file_name,
                    test_methods=test_methods_str,
                    class_name=test_class.class_name,
                    constants=constants_str
                )
            )
            if class_constants:
                (self.constants_path / file_name).write_text(
                    constants_templates.CONSTANTS_FILE_TEMPLATE.render(constants=class_constants)
                )
        (self.results_path / "locustfile.py").write_text(
            locustfile_templates.MAIN_FILE_TEMPLATE.render(
                security_cases=security_cases,
                host=swagger_data["host"],
                test_classes_names=test_classes.keys(),
                test_classes_imports=test_classes_imports
            )
        )
        (self.results_path / "helpers.py").write_text(helpers_templates.HELPER_CLASS_TEMPLATE.render())
        (self.constants_path / "base_constants.py").write_text(constants_templates.CONSTANTS_BASE_FILE_TEMPLATE.render())

    def generate_test_classes(self, paths_data: dict) -> Dict[str, TestClass]:
        """Method: generate test cases"""

        test_classes_mapping: Dict[str, TestClass] = {}
        for path, methods_data in paths_data.items():
            test_count = 0
            for method, method_data in methods_data.items():
                # responses_data = method_data.get("responses", {})
                try:
                    params = self.extract_params(method_data.get("params", {}))
                except ValueError as error:
                    logging.warning(error)
                    continue
                import re
                path_params_pattern = re.compile(r"{.*?}", re.UNICODE)
                identifier_pattern = re.compile(r"[^\d\w/]", re.UNICODE)
                test_name = re.sub(path_params_pattern, "", path)

                file_path = test_name.strip("/")
                file_path = re.sub(identifier_pattern, "_", file_path)
                file_path = file_path.split("/")

                file_name = file_path[-1]
                file_path = Path(*file_path[:-1])

                class_name = file_name.replace("_", " ")
                class_name = class_name.title()
                class_name = class_name.replace(" ", "")
                if not class_name.isidentifier():
                    class_name = "Test_" + class_name

                constants = []
                test_method_data = locustfile_templates.FUNC_TEMPLATE.render(
                    func_name=f"{file_name}_test_{test_count}",
                    method=method,
                    path=path,
                    # TODO test name -> file name
                    test_name=test_name,
                    path_params=self._format_params(params["path_params"], "path", constants),
                    query_params=self._format_params(params["query_params"], "query", constants),
                    header_params=self._format_params(params["header_params"], "header", constants),
                    cookie_params=self._format_params(params["cookie_params"], "cookie", constants),
                )
                test_method = TestMethod(method_data=test_method_data)
                test_method.constants += constants
                test_class = test_classes_mapping.get(class_name)
                if test_class is None:
                    test_class = TestClass(file_path=file_path, file_name=file_name, class_name=class_name)
                    test_classes_mapping[class_name] = test_class
                test_class.test_methods.append(test_method)
                test_count += 1
        return test_classes_mapping

    @staticmethod
    def extract_params(params: dict) -> Dict[str, list]:
        """Method: extract params"""

        path_params = []
        query_params = []
        header_params = []
        cookie_params = []
        for param, param_config in params.items():
            param_location = param_config.get("in")
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
            target_params.append(param_config)

        extracted_params = {
            "path_params": path_params,
            "query_params": query_params,
            "header_params": header_params,
            "cookie_params": cookie_params,
        }
        return extracted_params

    @staticmethod
    def _format_params(raw_params: List[dict], param_type, constants) -> Union[str, dict]:
        params = []
        for param in raw_params:
            name = param.get("name")
            const_name = name.upper()
            val = param.get("default")
            param_value_type = param.get("type")
            if val is None:
                const_val = helpers_templates.HELPER_MAPPING.get(param_value_type, "") + "()"
            else:
                const_val = repr(val)
            choice_helper = helpers_templates.HELPER_MAPPING["choice"]
            val = choice_helper + "(*" + const_name + ")"
            const = Constant(name=const_name, val=const_val, value_type=param_value_type)
            constants.append(const)
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
