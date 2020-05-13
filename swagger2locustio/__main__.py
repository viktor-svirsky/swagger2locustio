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
        loglevel = "DEBUG"
    else:
        loglevel = "INFO"
    coloredlogs.install(level=loglevel, fmt="%(asctime)s [%(levelname)s] %(filename)s: %(message)s")
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

    folders_amount, files_amount, classes_amount, functions_amount = 0, 0, 0, 0
    for root, dirs, files in os.walk(args.results_path):
        folders_amount += len(dirs)
        files_amount += len(files)
        for filename in files:
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
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
