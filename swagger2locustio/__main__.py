"""Module: This is main module that actvates library"""

import os
import json
import argparse
import logging
from pathlib import Path

import yaml
import coloredlogs
from swagger2locustio.strategy.base_strategy import BaseStrategy

API_OPERATIONS = ("get", "post", "put", "patch", "delete", "head", "options", "trace")


def main():
    """Launching function"""

    args = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args.add_argument("-f", "--swagger-file", help="path to swagger file", required=True, type=Path)
    args.add_argument(
        "-r",
        "--results-path",
        help="path to store locustfile.py",
        required=False,
        default=Path("generated"),
        type=Path,
    )
    args.add_argument(
        "-v", "--verbose", help="verbose", required=False, action="store_true", default=False,
    )
    args.add_argument(
        "-s",
        "--strict-level",
        help="add paths with required params without default values to locust tests",
        required=False,
        choices=(0, 1, 2),
        type=int,
        default=2,
    )
    args.add_argument(
        "-o",
        "--operations",
        help="operations to use in api testing",
        required=False,
        nargs="+",
        choices=API_OPERATIONS,
        default=["get"],
    )
    args.add_argument(
        "--paths-white", "--pw", help="paths to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    args.add_argument(
        "--paths-black", "--pb", help="paths not to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    args.add_argument(
        "--tags-white", "--tw", help="tags to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    args.add_argument(
        "--tags-black", "--tb", help="tags to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    args = args.parse_args()
    if args.verbose:
        loglevel = "DEBUG"
    else:
        loglevel = "INFO"
    coloredlogs.install(level=loglevel, fmt="%(asctime)s [%(levelname)s] %(filename)s: %(message)s")

    main_start = log_result(args.results_path)

    log = logging.getLogger(__name__)
    log.debug("Command line args: %s", args)
    swagger_file = args.swagger_file
    ext = swagger_file.suffix
    paths = [path.lower() for path in args.paths_white]
    not_paths = [path.lower() for path in args.paths_black]
    tags = [tag.lower() for tag in args.tags_white]
    not_tags = [tag.lower() for tag in args.tags_black]
    if paths and not_paths:
        raise ValueError("Both `paths` and not `paths` arguments specified")

    if tags and not_tags:
        raise ValueError("Both `tags` and not `not_tags` arguments specified")

    mask = {
        "operations_white_list": set(args.operations),
        "paths_white_list": set(paths),
        "paths_black_list": set(not_paths),
        "tags_white_list": set(tags),
        "tags_black_list": set(not_tags),
    }
    log.debug("Mask: %s", mask)

    if ext == ".json":
        with open(swagger_file) as file:
            swagger_data = json.load(file)
    elif ext in (".yaml", ".yml"):
        with open(swagger_file) as file:
            swagger_data = yaml.safe_load(file)
    else:
        raise ValueError("Incorrect file format")
    swagger_strategy = BaseStrategy(swagger_data, args.results_path, mask, args.strict_level)
    try:
        swagger_strategy.process()
    except ValueError as error:
        logging.error(error)

    log_diff(main_start, log_result(args.results_path), args.results_path)


def log_diff(start, end, results_path):
    """Function: log difference"""

    for key, items in start.items():
        start_key = set(items)
        end_key = set(end[key])
        result = {
            "created": [],
            "unchanged": [],
            "updated": [],
            "deleted": [],
        }

        # CREATED / DELETED
        result["created"] = list(end_key - start_key)
        result["deleted"] = list(start_key - end_key)

        # UNCHANGED / UPDATED
        if type(end[key]) == type(list()):
            result["unchanged"] = list(start_key.intersection(end_key))
        elif type(end[key]) == type(dict()):
            for each_start_key, each_start_data in items.items():
                for each_end_key, each_end_data in end[key].items():
                    if each_start_key == each_end_key and each_start_data == each_end_data:
                        # folder entries do not include \n, so last letter is being cut off
                        result["unchanged"].append(each_start_key)
                    elif each_start_key == each_end_key:
                        result["updated"].append(each_start_key)
                    # else is not used as we compare two lists which includes a lot of false entries

        for result_key in result:
            result[result_key].sort()
            result_len = len(result[result_key])
            if result_len != 0 and (key != "folders" or result_key != "updated"):
                logging.info("%s %s: %d", key.upper(), result_key, result_len)
                if result_key != "unchanged":
                    logging.debug("%s %s items:", key.upper(), result_key)
                    for each in result[result_key]:
                        logging.debug("    %s", each)

    logging.info("NOTE: Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    logging.info("NOTE: We also advise to check authorization settings")
    logging.debug("NOTE: All the paths mentioned use %s as root directory", results_path)


def log_result(results_path):
    """Function: log run results"""

    result = {
        "folders": [],
        "files": {},
        "classes": {},
        "functions": {},
    }
    results_path = str(results_path)

    for root, dirs, files in os.walk(results_path):
        result["folders"] += [os.path.join(root, x) for x in dirs]

        for filename in files:
            if filename[-3:] != ".py":
                continue

            file_path = os.path.join(root, filename)

            results_path = str(results_path)
            file_path_cleaned = str(file_path)
            if file_path_cleaned[: len(results_path)] == results_path:
                file_path_cleaned = file_path_cleaned[len(results_path) :]
            else:
                logging.warning("unknown path %s was mentioned", file_path_cleaned)

            with open(file_path, "r", encoding="utf-8") as file:
                result["files"][file_path_cleaned] = file.read()
                file.seek(0)

                file_class = ""
                file_function = ""
                for line in file:
                    if line.find("class ") != -1:
                        name = file_path_cleaned + ": " + line.lstrip()
                        name = name[: name.find("\n")] if "\n" in name else name
                        result["classes"][name] = line.lstrip()
                        file_class = name
                        file_function = ""
                    elif line.find("def ") != -1:
                        name = file_path_cleaned + ": " + line.lstrip()
                        name = name[: name.find("\n")] if "\n" in name else name
                        result["functions"][name] = line.lstrip()
                        file_function = name

                    if file_class != "":
                        result["classes"][file_class] += line
                    if file_function != "":
                        result["functions"][file_function] += line

    return result


if __name__ == "__main__":
    main()
