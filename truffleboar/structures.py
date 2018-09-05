
from typing import Dict, Any, Iterable, NamedTuple

# Regex Pattern class is only implemented in Python3.7
# For compatability reasons we will remain with 3.6 for now
Rules = Dict[str, Any]


class Artifact(NamedTuple):
    """
    An artifact is a positive match from a checker
    It contains a reason for the match and all found values
    """
    reason: str
    values: Iterable[str]

    # TODO: How can we customise the output?
    def __str__(self):
        formatted = f"Reason: {self.reason}\n"
        formatted += "\n".join(str(value) for value in self.values)
        return formatted


class Feature(NamedTuple):
    """
    A feature is an instance of a violation or match by one of the checkers
    The match itself (which can be one or more matches) is contained as an artifact
    The other information is metadata indicating the context of the artifact
    """

    date: str
    source: str
    section: str
    identifier: str
    location: str
    artifacts: Iterable[Artifact]

    # TODO: How can we customise the output?
    def __str__(self):
        formatted = (f"Date: {self.date}\n" 
                    f"Source: {self.source}\n"
                    f"Section: {self.section}\n"
                    f"ID: {self.identifier}\n"
                    f"Location: {self.location}\n"
                    "\n")

        formatted_artifacts = "\n".join(str(artfact) for artfact in self.artifacts)
        return formatted + formatted_artifacts + "\n\n"
