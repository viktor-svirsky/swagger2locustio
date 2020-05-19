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

    for key in start.keys():
        start_key = set(start[key])
        end_key = set(end[key])

        start_key_names = {x[: x.find("\n")] for x in start_key}
        end_key_names = {x[: x.find("\n")] for x in end_key}
        created = end_key_names - start_key_names
        deleted = start_key_names - end_key_names

        unchanged, updated = [], []
        for each_start in start_key:
            for each_end in end_key:
                if each_start == each_end:
                    unchanged.append(each_start[: each_start.find("\n")])
                elif each_start[: each_start.find("\n")] == each_end[: each_end.find("\n")]:
                    updated.append(each_start[: each_start.find("\n")])

        logging.info("%s CREATED: %s", key, len(created))
        logging.debug("%s CREATED items: %s", key, [x[: x.find("\n")] for x in created])
        logging.info("%s UNCHANGED: %s", key, len(unchanged))
        logging.debug("%s UNCHANGED items: %s", key, unchanged)
        logging.info("%s UPDATED: %s", key, len(updated))
        logging.debug("%s UPDATED items: %s", key, updated)
        logging.info("%s DELETED: %s", key, len(deleted))
        logging.debug("%s DELETED items: %s", key, [x[: x.find("\n")] for x in deleted])
        # logging.info("==== %s ====", key.upper())
        # if len(created) != 0:
        #     logging.info("created: %s", len(created))
        #     logging.debug("created items: %s", [x[: x.find("\n")] for x in created])
        # # if len(unchanged) != 0:
        # #     logging.info("unchanged: %s", len(unchanged))
        # #     logging.debug("unchanged items: %s", unchanged)
        # if len(updated) != 0:
        #     logging.info("updated: %s", len(updated))
        #     logging.debug("updated items: %s", updated)
        # if len(deleted) != 0:
        #     logging.info("deleted: %s", len(deleted))
        #     logging.debug("deleted items: %s", [x[: x.find("\n")] for x in deleted])
        # logging.info("")

    logging.info("NOTE: Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    logging.info("NOTE: We also advise to check authorization settings")
    logging.info("NOTE: Some class updates can be triggered by changes in order of items used due to set type usage")
    logging.debug("NOTE: All the paths mentioned use %s as root directory", results_path)
    # logging.info("==== NOTE: ====")
    # logging.info("- Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    # logging.info("- We also advise to check authorization settings")
    # logging.info("- Some class updates can be triggered by changes in order of items used due to set type usage")
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
        result["files"] += [os.path.join(root, x) for x in files]
        for filename in files:
            with open(os.path.join(root, filename), "r", encoding="utf-8") as file:
                for line in file:
                    if line.find("class ") != -1:
                        result["classes"].append(os.path.join(root, filename, line.lstrip()))
                    elif line.find("def ") != -1:
                        result["functions"].append(os.path.join(root, filename, line.lstrip()))
                    elif len(result["classes"]) > 0:
                        result["classes"][-1] += line
                    elif len(result["functions"]) > 0:
                        result["functions"][-1] += line

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


def log_result(results_path):
    """Function: log run results"""

    folders_amount, files_amount, classes_amount, functions_amount = 0, 0, 0, 0
    for root, dirs, files in os.walk(results_path):
        folders_amount += len(dirs)
        files_amount += len(files)
        for filename in files:
            with open(os.path.join(root, filename), "r", encoding="utf-8") as file:
                for line in file:
                    classes_amount += 1 if line.find("class ") != -1 else 0
                    functions_amount += 1 if line.find("def ") != -1 else 0

    logging.info("created folders: %s", str(folders_amount))
    logging.info("created files: %s", str(files_amount))
    logging.info("created classes: %s", str(classes_amount))
    logging.info("created functions: %s", str(functions_amount))
    logging.info("NOTE: Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    logging.info("NOTE: We also advise to check authorization settings")


if __name__ == "__main__":
    main()
