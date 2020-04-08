import argparse
from pathlib import Path

from swagger2locustio.strategy.json_strategy import JsonStrategy

API_OPERATIONS = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--swagger_file",
        help="path to swagger file",
        required=True,
        type=Path
    )
    parser.add_argument(
        "--results_path",
        help="path to store locustfile.py",
        required=False,
        default=Path("generated"),
        type=Path
    )
    parser.add_argument(
        "--strict",
        help="add paths with required params without default values to locust tests",
        required=False,
        default=False,
        type=bool
    )
    parser.add_argument(
        "--operations",
        help="operations to use in api testing",
        required=False,
        nargs="+",
        choices=API_OPERATIONS,
        default=["get"]
    )
    parser.add_argument(
        "--paths",
        help="paths to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    parser.add_argument(
        "--not-paths",
        help="paths not to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    parser.add_argument(
        "--tags",
        help="tags to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    parser.add_argument(
        "--not-tags",
        help="tags to use in api testing",
        required=False,
        nargs="+",
        type=str,
        default=[]
    )
    args = parser.parse_args()
    swagger_file = args.swagger_file
    results_path = args.results_path
    ext = swagger_file.suffix
    operations = args.operations
    paths = [path.lower() for path in args.paths]
    not_paths = [path.lower() for path in args.not_paths]
    tags = [tag.lower() for tag in args.tags]
    not_tags = [tag.lower() for tag in args.not_tags]

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

    if ext == ".json":
        swagger_strategy = JsonStrategy(swagger_file, results_path, mask, args.strict)
    elif ext in (".yaml", ".yml"):
        swagger_strategy = ellipsis
    else:
        raise ValueError("Incorrect file format")
    swagger_strategy.process()


if __name__ == "__main__":
    main()
