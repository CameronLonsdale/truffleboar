"""Utility module"""

import json
import re
import tempfile
import git

from .structures import Rules

from typing import Iterable


def load_rules(json_file_path: str) -> Rules:
    """
    Load rules from a JSON file
    """
    try:
        with open(json_file_path, "r") as rules_file:
            rules = json.load(rules_file)
            return {name: re.compile(regex) for name, regex in rules.items()}
    # TODO split this into more specific errors
    except (IOError, ValueError):
        raise ValueError("Invalid rules file")


def clone_git_repo(git_url):
    project_path = tempfile.mkdtemp()
    git.Repo.clone_from(git_url, project_path)
    return project_path


def get_strings_of_set(text: str, char_set: Iterable[str], threshold_length: int) -> Iterable[str]:
    """
    Find strings constructed from consecutive letters in char_set. Only return strings
    greater than or equal to threshold_length
    """
    count = 0
    letters = ""
    strings = []

    for char in text:
        if char in char_set:
            letters += char
            count += 1
        else:
            if count > threshold_length:
                strings.append(letters)
            letters = ""
            count = 0

    if count > threshold_length:
        strings.append(letters)

    return strings
