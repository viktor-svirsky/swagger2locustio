"""Module: Base Generator"""

import re
import logging
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Union, Any

from swagger2locustio.templates import locustfile_templates as l_templates
from swagger2locustio.templates import helpers_templates
from swagger2locustio.templates import auth_templates
from swagger2locustio.templates import constants_templates

LOG = logging.getLogger(__name__)

PATH_PARAMS_PATTERN = re.compile(r"{.*?}", re.UNICODE)
IDENTIFIER_PATTERN = re.compile(r"[^\d\w/]", re.UNICODE)


@dataclass(frozen=True, order=True)
class Constant:
    """Data Class: Constant"""

    name: str
    val: Any
    value_type: str


@dataclass
class TestMethod:
    """Data Class: Test Method"""

    method_data: str
    constants: List[Constant]


@dataclass
class TestClass:
    """Data Class: Test Class"""

    file_path: Path
    file_name: str
    class_name: str
    test_methods: List[TestMethod] = field(default_factory=lambda: [])


class BaseGenerator:
    """Class: Base Generator"""

    def __init__(self, results_path: Path):
        self.swagger_data = {}
        self.test_classes_mapping: Dict[str, TestClass] = {}
        self.results_path = results_path
        self.apps_path = Path("apps")
        constants_path = Path("constants")
        self.app_name = self.get_app_name()
        self.current_app_path = self.apps_path / self.app_name
        self.tests_path = self.current_app_path / "tasksets" / "generated_tests"
        self.current_app_constants_path = self.current_app_path / "constants"
        (self.results_path / self.tests_path).mkdir(exist_ok=True,
                                                    parents=True)
        (self.results_path / constants_path).mkdir(exist_ok=True, parents=True)
        (self.results_path / self.current_app_constants_path).mkdir(
            exist_ok=True, parents=True)
        (self.results_path / constants_path / "base_constants.py").write_text(
            constants_templates.CONSTANTS_BASE_FILE.render())
        (self.results_path / self.apps_path / "helper.py").write_text(
            helpers_templates.HELPER_CLASS.render())

    def get_app_name(self):
        """Method: returns app name"""
        apps = []
        counter = 0
        dir_name = f"app{counter}"
        while (self.results_path / self.apps_path / dir_name).exists():
            apps.append(dir_name)
            counter += 1
            dir_name = f"app{counter}"
        LOG.info("Existed apps: %s", apps)
        prompt = f"Type name of created app - to update it, or name of new app, or press Enter to use `{dir_name}`:\n"
        user_input = input(prompt)
        while user_input != "" and not user_input.isidentifier():
            LOG.warning("Name should be valid python identifier")
            user_input = input(prompt)
        if user_input != "":
            dir_name = user_input
        return dir_name

    def generate_locustfiles(self, swagger_data: dict) -> None:
        """Method: generate locustfiles"""
        self.swagger_data = swagger_data
        self.generate_test_classes(swagger_data["paths"])
        security_cases = self.generate_security_cases(swagger_data["security"])
        test_classes_imports = []
        test_classes_inheritance = []
        for test_class in self.test_classes_mapping.values():
            methods_count = len(test_class.test_methods)
            if not methods_count:
                continue
            class_methods = []
            class_constants = []
            for test_method in test_class.test_methods:
                class_methods.append(test_method.method_data)
                class_constants.extend(test_method.constants)
            methods_str = "".join(class_methods)
            class_file_path = self.results_path / self.tests_path / test_class.file_path
            class_file_path.mkdir(parents=True, exist_ok=True)
            file_name = f"{test_class.file_name}.py"
            class_constants = list(sorted(set(class_constants)))
            constants_str = ", ".join(
                [constant.name for constant in class_constants])
            import_path = str(self.tests_path / test_class.file_path /
                              test_class.file_name).replace("/", ".")
            test_classes_imports.append(
                f"from {import_path} import {test_class.class_name}")
            test_classes_inheritance.append(test_class.class_name)
            (class_file_path / file_name).write_text(
                l_templates.TEST_CLASS_FILE.render(
                    file_name=test_class.file_name,
                    test_methods=methods_str,
                    class_name=test_class.class_name,
                    constants=constants_str,
                    app_name=self.app_name,
                ))
            if class_constants:
                (self.results_path / self.current_app_constants_path /
                 file_name).write_text(
                     constants_templates.CONSTANTS_FILE.render(
                         constants=class_constants))
        (self.results_path / "locustfile.py").write_text(
            l_templates.MAIN_LOCUSTFILE.render(
                host=swagger_data["host"],
                app_name=self.app_name,
            ))
        (self.results_path / self.current_app_path /
         "generated_taskset.py").write_text(
             l_templates.GENERATED_TASKSET_FILE.render(
                 test_classes_names=test_classes_inheritance,
                 test_classes_imports=test_classes_imports,
             ))
        (self.results_path / self.apps_path / "base.py").write_text(
            l_templates.BASE_TASKSET_FILE.render(
                security_cases=security_cases, ))
        LOG.info("%s test methods were created successfully",
                 len(test_classes_inheritance))

    def _get_or_create_test_class(self, ulr_path: str) -> TestClass:
        file_path_str = re.sub(PATH_PARAMS_PATTERN, "", ulr_path)
        file_path_str = file_path_str.strip("/")
        file_path_str = re.sub(IDENTIFIER_PATTERN, "_", file_path_str)
        file_path_list = file_path_str.split("/")
        file_name = file_path_list[-1]
        file_path = Path(*file_path_list[:-1])
        if not file_name.isidentifier():
            file_name = "test_" + file_name
        file_name = file_name.replace("_", " ")
        file_name = file_name.title()
        class_name = file_name.replace(" ", "")
        file_name = file_name.replace(" ", "_")

        test_class = self.test_classes_mapping.get(class_name)
        if test_class is None:
            test_class = TestClass(file_path=file_path,
                                   file_name=file_name,
                                   class_name=class_name)
            self.test_classes_mapping[class_name] = test_class
        return test_class

    def generate_test_classes(self, paths_data: dict) -> None:
        """Method: generate test cases"""

        for ulr_path, methods_data in paths_data.items():
            test_class = self._get_or_create_test_class(ulr_path)

            for method, method_data in methods_data.items():
                # responses_data = method_data.get("responses", {})
                constants: List[Constant] = []
                try:
                    params = self.extract_params(method_data.get("params", {}),
                                                 constants,
                                                 len(test_class.test_methods))
                except ValueError as error:
                    logging.warning(error)
                    continue
                test_method_data = l_templates.FUNC.render(
                    func_name=
                    f"{test_class.file_name.lower()}_test_{len(test_class.test_methods)}",
                    method=method,
                    path=ulr_path,
                    path_params=params["path_params"],
                    query_params=params["query_params"],
                    header_params=params["header_params"],
                    cookie_params=params["cookie_params"],
                    body_params=params["body_params"]
                )
                test_class.test_methods.append(
                    TestMethod(method_data=test_method_data,
                               constants=constants))

    def extract_params(self, params: dict, constants: List[Constant],
                       method_num: int) -> Dict[str, Union[str, dict]]:
        """Method: extract params"""
        path_params: List[dict] = []
        query_params: List[dict] = []
        header_params: List[dict] = []
        cookie_params: List[dict] = []
        body_params: dict = {}
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
            elif param_location == "body":
                properties_key = param_config.get('schema').get('originalRef')
                definitions = self.swagger_data.get("definitions")
                properties = definitions.get(properties_key).get('properties')
                body_params = self.reassemble_properties(
                    properties, definitions)
                target_params = []
            else:
                raise ValueError(
                    f"Not valid {param} `in` value: {param_location}",
                    param_config)
            target_params.append(param_config)

        extracted_params = {
            "path_params":
            self._format_params(path_params, "path", constants, method_num),
            "query_params":
            self._format_params(query_params, "query", constants, method_num),
            "header_params":
            self._format_params(header_params, "header", constants,
                                method_num),
            "cookie_params":
            self._format_params(cookie_params, "cookie", constants,
                                method_num),
            "body_params": json.dumps(body_params)
        }
        return extracted_params

    def reassemble_properties(self, properties: dict, definitions: dict):

        new_properties = {}
        for key, value in properties.items():
            if isinstance(value, dict) and '$ref' in value:
                ref_key = value.get('originalRef')
                new_properties[key] = self.reassemble_properties(
                    definitions.get(ref_key).get('properties'), definitions)
            else:
                new_properties[key] = value.get('type')

        return new_properties

    @staticmethod
    def _format_params(raw_params: List[dict], param_type, constants,
                       method_num: int) -> Union[str, dict]:
        params = []
        for param in raw_params:
            param_name = param.get("name", "")
            const_name = param_name.upper() + f"__{method_num}"
            param_val = param.get("default")
            param_val_type = param.get("type", "")
            const_val = repr(param_val)
            if param_val is None:
                const_val = helpers_templates.HELPER_MAPPING.get(
                    param_val_type, "")
            param_val = helpers_templates.HELPER_MAPPING["choice"].format(
                values=const_name)
            constants.append(
                Constant(name=const_name,
                         val=const_val,
                         value_type=param_val_type))
            if param_type == "path":
                params.append(
                    l_templates.PATH_PARAM_PAIR.render(key=param_name,
                                                       val=param_val))
            else:
                params.append(
                    l_templates.DICT_PARAM_PAIR.render(key=param_name,
                                                       val=param_val))
        if param_type == "path":
            formatted_params = ""
            if params:
                formatted_params = ", " + ", ".join(params)
        else:
            formatted_params = "{}"
            if params:
                formatted_params = "{" + ", ".join(params) + "}"
        return formatted_params

    @staticmethod
    def generate_security_cases(security_data: dict) -> str:
        """Method: generate security cases"""

        security_cases = []
        for security_type, security_config in security_data.items():
            if security_type == "basic":
                security_cases.append(
                    auth_templates.AUTH_BASIC.render(
                        security_config=security_config))
            elif security_type == "apiKey":
                location = security_config.get("in")
                name = security_config.get("name")
                if location.lower() == "header" and name:
                    security_cases.append(
                        auth_templates.AUTH_KEY_HEADER.render(
                            name=name, security_config=security_config))
                else:
                    raise ValueError(security_config)
            else:
                security_cases.append(
                    auth_templates.AUTH_UNDEFINED.render(
                        security_config=security_config))
        return "".join(security_cases)
