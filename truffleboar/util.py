"""Utility module"""

import json
import re
import tempfile
import git

from .structures import Rules


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
