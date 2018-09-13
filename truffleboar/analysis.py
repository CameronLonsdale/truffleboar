"""
Analysis module

These functions perform the actual analysis to determine if a feature has been found
"""

import math

from truffleboar.structures import Rules, Artifact
from truffleboar import util

from typing import Optional, Iterable


BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
HEX_CHARS = "1234567890abcdefABCDEF"


def regex_check(text: Optional[str], patterns: Rules) -> Optional[Iterable[Artifact]]:
    """
    Check text for rule matches specified by patterns
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


def _shannon_entropy(data: Optional[str], char_set: Iterable[str]) -> float:
    """
    Calculate the shannon entropy for a given string
    Borrowed from http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html
    """

    if not data:
        return 0

    entropy = 0
    for x in char_set:
        p_x = float(data.count(x))/len(data)
        if p_x > 0:
            entropy += - p_x*math.log(p_x, 2)

    return entropy


def entropy_check(text: Optional[str], string_length_threshold: int = 20, b64entropy_threshold: float = 4.5, hexentropy_threshold: float = 3) -> Optional[Iterable[Artifact]]:
    """
    Check text for high entropy strings
    """
    artifacts = []

    for line in text.split("\n"):
        for word in line.split():
            base64_strings = util.get_strings_of_set(word, BASE64_CHARS, string_length_threshold)
            hex_strings = util.get_strings_of_set(word, HEX_CHARS, string_length_threshold)

            for string in base64_strings:
                b64Entropy = _shannon_entropy(string, BASE64_CHARS)
                if b64Entropy > b64entropy_threshold:
                    artifacts.append(Artifact(
                        reason="High Entropy String",
                        values=[string]
                    ))

            for string in hex_strings:
                hexEntropy = _shannon_entropy(string, HEX_CHARS)
                if hexEntropy > hexentropy_threshold:
                    artifacts.append(Artifact(
                        reason="High Entropy String",
                        values=[string]
                    ))

    return artifacts
