#!/usr/bin/env python

import argparse
import truffleboar

from typing import Dict, Any, NamedTuple, Iterable, Optional


def main() -> None:
    """Command line interface for truffleboar"""
    parser = argparse.ArgumentParser(description="Find secrets hidden in a GitHub repository")
    parser.add_argument("--rules", type=str, help="Ignore default regexes and source from json list file")
    parser.add_argument("--branch", type=str, help="Name of the branch to be scanned")
    parser.add_argument("--token", type=str, help="GitHub token for API requests")
    parser.add_argument("project_full_name", type=str, help='Full name of project to search for secrets')
    args = parser.parse_args()

    rules = truffleboar.load_rules(args.rules) if args.rules else truffleboar.default_rules

    features = truffleboar.find_features(
        project_full_name=args.project_full_name,
        custom_regexes=rules,
        branch=args.branch,
        auth_token=args.token
    )

    for feature in features:
        print(feature)


if __name__ == "__main__":
    main()
