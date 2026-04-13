from __future__ import annotations

from enum import StrEnum


class Complexity(StrEnum):
    SIMPLE = "simple"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class PromptLevel(StrEnum):
    VAGUE = "vague"
    SPECIFIC = "specific"
    VERY_SPECIFIC = "very_specific"


class Environment(StrEnum):
    OPEN = "open"
    GALAXY = "galaxy"
    GALAXY_SKILLS = "galaxy_skills"


class RunStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
