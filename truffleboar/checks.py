"""Checks module

These functions perform the actual check to determine if a feature has been found
"""

from truffleboar.structures import Rules, Artifact
from typing import Optional, Iterable


def regex_check(text: Optional[str], patterns: Rules) -> Optional[Iterable[Artifact]]:
    """
    Check text for rule matches specified by patterns.
    Return these matches in a list of Artifacts
    """
    artifacts = []

    if not text:
        return None

    for name, regex in patterns.items():
        matches = regex.findall(text)

        if matches:
            artifacts.append(Artifact(
                reason=name,
                values=matches
            ))

    return artifacts