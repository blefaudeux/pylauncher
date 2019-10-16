#!/usr/bin/env python3

import argparse
from pathlib import Path
import json
import subprocess
from typing import List

_DEFAULT_CONFIG = [{"command": "echo", "output_extension": ""}]
_KEYS = ["command", "input_extension", "output_extension"]
_SUBS = ["${filename}", "${filepath}"]

# Ideas for new options:
# "recursive" - go through the subfolders
# "parallel" - run the command on all files in parallel


def get_files(filepath, extension):
    pass


def load_config(config_path):
    # Sanitize: check that config is a json
    with open(config_path, "r") as conf_io:
        try:
            config = json.load(conf_io)
        except ValueError:
            print("Failed parsing the config file, is that really Json ?")
            exit(-1)

    # Check that we know all the keys in the config
    for l in config:
        for k in l.keys():
            if k not in _KEYS:
                print(f"Unknown keyword: {k}. Will not be applied\n")

    print(f"Using config:\n{config}")
    return config


def substitute(command: List[str], file: Path) -> List[str]:
    """
    Given the original command, substitute the known keywords
    """

    # Replace all ${filename} by the corresponding value
    command = list(map(lambda x: x.replace("${filename}", str(file.stem)), command))

    # Replace all ${filepath} by the corresponding value
    command = list(
        map(lambda x: x.replace("${filepath}", str(file.resolve())), command)
    )

    return command


def process(args):
    # Sanitize: check paths
    config_path = Path(args.config_path)
    folder_path = Path(args.folder_path)

    if not config_path.is_file():
        print(f"Could not read {config_path}, file does not exist")

    if not folder_path.is_dir():
        print(f"Could not read {folder_path}, directory does not exist")

    config = load_config(config_path)

    # Unroll all the actions
    for actions in config:
        # Get all the corresponding files
        try:
            file_list = list(
                filter(
                    lambda f: f.suffix == actions["input_extension"],
                    folder_path.iterdir(),
                )
            )

            print(
                "Found the following files to process:\n{}".format(
                    [str(p) for p in file_list]
                )
            )
        except KeyError:
            print("Cannot apply this command to files")

        command = actions["command"].split(" ")

        for f in file_list:
            # Substitute eventual filename in the command
            _command = substitute(command, f)

            # Run the command.
            # TODO: @lefaudeux Catch possible errors from there
            # and cook a report
            subprocess.run(_command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path", type=str, help="Path to the config json")

    parser.add_argument(
        "--dump_default",
        type=bool,
        default=False,
        help="Generate a default config Json",
        required=False,
    )

    parser.add_argument(
        "--folder_path",
        type=str,
        help="Folder containing the files that you would like to process",
    )

    args = parser.parse_args()
    process(args)
