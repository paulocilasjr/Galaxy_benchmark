"""Domain-specific exceptions."""

from __future__ import annotations


class GalaxyBenchmarkError(Exception):
    """Base error for the benchmark platform."""


class ArtifactAlreadyExistsError(GalaxyBenchmarkError):
    """Raised when an immutable artifact path is written twice."""


class LegacyMigrationError(GalaxyBenchmarkError):
    """Raised when a legacy experiment cannot be migrated safely."""
