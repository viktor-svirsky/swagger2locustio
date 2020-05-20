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

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--swagger-file", help="path to swagger file", required=True, type=Path)
    parser.add_argument(
        "-r",
        "--results-path",
        help="path to store locustfile.py",
        required=False,
        default=Path("generated"),
        type=Path,
    )
    parser.add_argument(
        "-v", "--verbose", help="verbose", required=False, action="store_true", default=False,
    )
    parser.add_argument(
        "-s",
        "--strict-level",
        help="add paths with required params without default values to locust tests",
        required=False,
        choices=(0, 1, 2),
        type=int,
        default=2,
    )
    parser.add_argument(
        "-o",
        "--operations",
        help="operations to use in api testing",
        required=False,
        nargs="+",
        choices=API_OPERATIONS,
        default=["get"],
    )
    parser.add_argument(
        "--paths-white", "--pw", help="paths to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    parser.add_argument(
        "--paths-black", "--pb", help="paths not to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    parser.add_argument(
        "--tags-white", "--tw", help="tags to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    parser.add_argument(
        "--tags-black", "--tb", help="tags to use in api testing", required=False, nargs="+", type=str, default=[]
    )
    args = parser.parse_args()
    if args.verbose:
        coloredlogs.install(level="DEBUG", fmt="%(asctime)s [%(levelname)s] %(filename)s: %(message)s")
    else:
        coloredlogs.install(level="INFO", fmt="%(asctime)s [%(levelname)s] %(filename)s: %(message)s")

    main_start = log_result_named(args.results_path)

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

    log_diff(main_start, log_result_named(args.results_path), args.results_path)
    # log_result(args.results_path)


def log_diff(start, end, results_path):
    """Function: log difference"""

    for key, items in start.items():

        result = {
            "created": [],
            "unchanged": [],
            "updated": [],
            "created": [],
        }
        
        start_key = set(items)
        end_key = set(end[key])

        start_key_names = {x[: x.find("\n")] if x.find("\n") != -1 else x for x in start_key}
        end_key_names = {x[: x.find("\n")] if x.find("\n") != -1 else x for x in end_key}
        result["created"] = list(end_key_names - start_key_names)
        result["deleted"] = list(start_key_names - end_key_names)

        for each_start in start_key:
            for each_end in end_key:
                if each_start == each_end:
                    result["unchanged"].append(
                        each_start[: each_start.find("\n")] if each_start.find("\n") != -1 else each_start
                    )
                elif each_start[: each_start.find("\n")] == each_end[: each_end.find("\n")]:
                    result["updated"].append(each_start[: each_start.find("\n")])

        for result_key in result:
            result[result_key].sort()
            result_len = len(result[result_key])
            if result_len != 0 and (key != "folders" or result_key != "updated"):
                logging.info("%s %s: %s", key.upper(), result_key, result_len)
                if result_key != "unchanged":
                    logging.debug("%s %s items:", key.upper(), result_key)
                    for each in result[result_key]:
                        logging.debug("    %s", each)

    logging.info("NOTE: Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    logging.info("NOTE: We also advise to check authorization settings")
    logging.debug("NOTE: All the paths mentioned use %s as root directory", results_path)
    # logging.info("==== NOTE: ====")
    # logging.info("- Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    # logging.info("- We also advise to check authorization settings")
    # logging.debug("- All the paths mentioned use %s as root directory", results_path)


def log_result_named(results_path):
    """Function: log run results"""

    result = {
        "folders": [],
        "files": [],
        "classes": [],
        "functions": [],
    }

    for root, dirs, files in os.walk(results_path):
        result["folders"] += [os.path.join(root, x) for x in dirs]
        
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                result["files"].append(file_path +"\n"+ file.read())
                file.seek(0)

                file_class = -1
                file_function = -1
                for line in file:
                    if line.find("class ") != -1:
                        result["classes"].append(file_path +": "+ line.lstrip())
                        file_class = len(result["classes"])-1
                    elif line.find("def ") != -1:
                        result["functions"].append(file_path +": "+ line.lstrip())
                        file_function = len(result["functions"])-1
                    elif file_class >= 0:
                        result["classes"][file_class] += line
                    elif file_function >= 0:
                        result["functions"][file_function] += line

    results_path = str(results_path)
    results_path_len = len(results_path)
    for key in result.keys():
        for index, file_path in enumerate(result[key]):
            if file_path[:results_path_len] == results_path:
                file_path = file_path[results_path_len:]
            else:
                logging.warning("unknown path %s was mentioned", file_path)

            result[key][index] = file_path

    return result


if __name__ == "__main__":
    main()
