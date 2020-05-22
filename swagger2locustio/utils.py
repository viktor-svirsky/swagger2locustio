"""Module: Utils"""

import os
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)


def changed_files_user_check(existed_files, new_files, results_path):
    """Function: changed files user check"""

    for file_name, old_data in existed_files.items():
        new_data = new_files.get(file_name, "")
        if old_data != new_data:
            LOG.warning("%s file has been changed. Do you want to overwrite it? [Y/any key]", file_name)
            user_input = input()
            if user_input not in ("y", "Y"):
                Path(str(results_path) + file_name).write_text(old_data)
            if file_name == "/locustfile.py":
                LOG.warning("NOTE: You should include imports to all apps tasksets yourself in `locustfile.py`")


def log_diff(start, end, results_path):
    """Function: log difference"""

    changed_files_user_check(start["files"], end["files"], results_path)

    for key, items in start.items():
        start_key = set(items)
        end_key = set(end[key])
        result = {
            "created": list(end_key - start_key),
            "unchanged": [],
            "updated": [],
            "deleted": list(start_key - end_key),
        }

        # UNCHANGED / UPDATED
        for each_start_key, each_start_data in items.items():
            for each_end_key, each_end_data in end[key].items():
                if each_start_key == each_end_key and each_start_data == each_end_data:
                    result["unchanged"].append(each_start_key)
                elif each_start_key == each_end_key:
                    result["updated"].append(each_start_key)
                # else is not used as we compare two lists which includes a lot of false entries

        for result_key in result:
            result[result_key].sort()
            result_len = len(result[result_key])
            if result_len != 0:
                LOG.info("%s %s: %d", key.upper(), result_key, result_len)
                LOG.debug("%s %s items:", key.upper(), result_key)
                for each in result[result_key]:
                    LOG.debug("    %s", each)

    LOG.warning("NOTE: Please make sure to fill in the constant files. Feel free to use helper functions to do it")
    LOG.warning("NOTE: We also advise to check authorization settings")
    LOG.debug("NOTE: All the paths mentioned use %s as root directory", results_path)


def log_result(results_path):
    """Function: log run results"""

    result = {
        "folders": {},
        "files": {},
        "classes": {},
        "functions": {},
    }
    results_path = str(results_path)

    for root, dirs, files in os.walk(results_path):
        result["folders"].update({os.path.join(root, folder): "" for folder in dirs})

        for filename in files:
            if filename[-3:] != ".py":
                continue

            file_path = os.path.join(root, filename)

            results_path = str(results_path)
            file_path_cleaned = str(file_path)
            if file_path_cleaned[: len(results_path)] == results_path:
                file_path_cleaned = file_path_cleaned[len(results_path) :]
            else:
                LOG.warning("unknown path %s was mentioned", file_path_cleaned)

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
