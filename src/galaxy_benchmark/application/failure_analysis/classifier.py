"""Failure classification services."""

from __future__ import annotations

import re

from galaxy_benchmark.domain.enums import FailureCategory
from galaxy_benchmark.domain.models import FailureEvidence


class ErrorSignatureBuilder:
    """Build stable error signatures from failure evidence."""

    def build(self, evidence: FailureEvidence) -> str:
        normalized = re.sub(r"\s+", " ", evidence.message).strip().lower()
        prefix = f"{evidence.step}:{evidence.exit_code if evidence.exit_code is not None else 'na'}"
        return f"{prefix}:{normalized[:120]}"


class FailureClassifier:
    """Assign a deterministic failure category from evidence text."""

    _keyword_map = {
        FailureCategory.POLLING_OR_WAITING: ("timeout", "poll", "waiting"),
        FailureCategory.PARAMETER_GROUNDING: ("parameter", "invalid value", "option"),
        FailureCategory.INPUT_MAPPING: ("dataset", "input", "path"),
        FailureCategory.WORKFLOW_DISCOVERY: ("workflow", "not found"),
        FailureCategory.TOOL_DISCOVERY: ("tool", "not found"),
        FailureCategory.OUTPUT_INTERPRETATION: ("report", "parse", "output"),
        FailureCategory.KNOWLEDGE_RETRIEVAL_FAILURE: ("gtn", "iwc", "tutorial"),
        FailureCategory.UNSUPPORTED_CAPABILITY: ("unsupported", "not implemented"),
    }

    def classify(self, evidence: FailureEvidence) -> FailureCategory:
        message = evidence.message.lower()
        for category, keywords in self._keyword_map.items():
            if any(keyword in message for keyword in keywords):
                return category
        return FailureCategory.UNKNOWN


class RecoveryAssessmentService:
    """Assess whether a rerun changed the failure signature."""

    @staticmethod
    def signature_changed(previous_signature: str, next_signature: str) -> bool:
        return previous_signature != next_signature
