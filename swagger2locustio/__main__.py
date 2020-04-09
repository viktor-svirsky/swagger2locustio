import argparse
import logging
from pathlib import Path

from swagger2locustio import settings
from swagger2locustio.strategy.json_strategy import JsonStrategy


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--swagger-file",
        help="path to swagger file",
        required=True,
        type=Path
    )
    parser.add_argument(
        "--results-path",
        help="path to store locustfile.py",
        required=False,
        default=Path("generated"),
        type=Path
    )
    parser.add_argument(
        "--loglevel",
        help="logging level",
        required=False,
        default="info",
        choices=settings.LOGGING_LEVELS,
        type=str
    )
    parser.add_argument(
        "--strict",
        help="add paths with required params without default values to locust tests",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--operations",
        help="operations to use in api testing",
        required=False,
        nargs="+",
        choices=settings.API_OPERATIONS,
        default=["get"]
    )
    parser.add_argument(
        "--paths-white",
        help="paths to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    parser.add_argument(
        "--paths-black",
        help="paths not to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    parser.add_argument(
        "--tags-white",
        help="tags to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    parser.add_argument(
        "--tags-black",
        help="tags to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    args = parser.parse_args()
    settings.config_logger(args.loglevel.upper())
    log = logging.getLogger(__name__)
    log.debug(f"Command line args: {args}")
    swagger_file = args.swagger_file
    results_path = args.results_path
    ext = swagger_file.suffix
    operations = args.operations
    paths = [path.lower() for path in args.paths_white]
    not_paths = [path.lower() for path in args.paths_black]
    tags = [tag.lower() for tag in args.tags_white]
    not_tags = [tag.lower() for tag in args.tags_black]
    if paths and not_paths:
        raise ValueError("Both `paths` and not `paths` arguments specified")

    if tags and not_tags:
        raise ValueError("Both `tags` and not `not_tags` arguments specified")

    mask = {
        "operations_white_list": set(operations),
        "paths_white_list": set(paths),
        "paths_black_list": set(not_paths),
        "tags_white_list": set(tags),
        "tags_black_list": set(not_tags)
    }
    log.debug(f"Mask: {mask}")

    if ext == ".json":
        swagger_strategy = JsonStrategy(swagger_file, results_path, mask, args.strict)
    elif ext in (".yaml", ".yml"):
        swagger_strategy = Ellipsis
    else:
        raise ValueError("Incorrect file format")
    log.debug(f"Strategy: {swagger_strategy}")
    try:
        swagger_strategy.process()
    except ValueError as e:
        logging.error(e)


if __name__ == "__main__":
    main()
