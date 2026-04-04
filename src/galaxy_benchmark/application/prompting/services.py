"""Prompt generation services."""

from __future__ import annotations

import re
from pathlib import Path

from galaxy_benchmark.domain.enums import PromptFormat, PromptTier
from galaxy_benchmark.domain.models import BenchmarkTask, PromptVariant


class PromptNormalizationService:
    """Deterministically normalize generated prompt content."""

    @staticmethod
    def normalize(content: str) -> str:
        normalized_lines: list[str] = []
        previous_blank = False
        for raw_line in content.strip().splitlines():
            line = re.sub(r"[ \t]+", " ", raw_line).strip()
            if not line:
                if not previous_blank:
                    normalized_lines.append("")
                previous_blank = True
                continue
            normalized_lines.append(line)
            previous_blank = False
        return "\n".join(normalized_lines).strip()


class PromptTemplateRepository:
    """Filesystem-backed prompt template loader with deterministic fallbacks."""

    _default = (
        "Task\n"
        "{task_block}\n\n"
        "Attachments\n"
        "{attachments_block}\n\n"
        "Suggested Galaxy Resources\n"
        "{resources_block}\n\n"
        "Requirements\n"
        "{requirements_block}\n\n"
        "Return\n"
        "{return_block}"
    )

    def __init__(self, root: Path | str = Path("benchmark/prompts")) -> None:
        self.root = Path(root)

    def load(self, prompt_format: PromptFormat) -> str:
        template_path = self.root / "template.txt"
        if template_path.exists():
            return template_path.read_text()
        return self._default


class PromptVariantGenerator:
    """Generate prompt variants across tiers and formats."""

    _tier_requirements = {
        PromptTier.NOVICE: [
            "Work step by step in Galaxy and state the main tool or workflow choice.",
            "Name the main parameters you set and explain any non-default setting.",
            "If a run fails, inspect the failure and retry only with a justified fix.",
        ],
        PromptTier.INTERMEDIATE: [
            "Choose a valid Galaxy workflow or tool path and name only decisive parameters.",
            "Use reasonable defaults when the task does not specify them.",
            "Verify the final artifacts before reporting the requested fields.",
        ],
        PromptTier.EXPERT: [
            "Take the shortest valid Galaxy path that satisfies the task.",
            "Mention only decisive tool or workflow choices and non-default parameters.",
            "Report the requested fields from the successful final run.",
        ],
    }

    def __init__(
        self,
        normalizer: PromptNormalizationService | None = None,
        templates: PromptTemplateRepository | None = None,
    ) -> None:
        self._normalizer = normalizer or PromptNormalizationService()
        self._templates = templates or PromptTemplateRepository()

    def generate(self, task: BenchmarkTask) -> list[PromptVariant]:
        variants: list[PromptVariant] = []
        for tier in PromptTier:
            for prompt_format in PromptFormat:
                content = self._render(task, tier, prompt_format)
                variants.append(
                    PromptVariant(
                        variant_id=f"{task.task_id}_{tier.value}_{prompt_format.value}",
                        task_id=task.task_id,
                        tier=tier,
                        format=prompt_format,
                        content=self._normalizer.normalize(content),
                    )
                )
        return variants

    def _render(self, task: BenchmarkTask, tier: PromptTier, prompt_format: PromptFormat) -> str:
        template = self._templates.load(prompt_format)
        return template.format(
            task_block=self._task_block(task, tier),
            attachments_block=self._attachments_block(task),
            resources_block=self._resources_block(task),
            requirements_block=self._requirements_block(task, tier),
            return_block=self._return_block(task),
        )

    def _task_block(self, task: BenchmarkTask, tier: PromptTier) -> str:
        intro_map = {
            PromptTier.NOVICE: "Complete the task in Galaxy using the provided files.",
            PromptTier.INTERMEDIATE: "Complete the task in Galaxy and produce the required outputs.",
            PromptTier.EXPERT: "Execute the task in Galaxy and report the required outputs.",
        }
        return f"{intro_map[tier]}\n- Objective: {task.description}"

    @staticmethod
    def _attachments_block(task: BenchmarkTask) -> str:
        if not task.input_assets:
            return "- None"
        return "\n".join(
            f"- {asset.name} ({asset.role}; {asset.format})"
            for asset in task.input_assets
        )

    @staticmethod
    def _resource_lines(task: BenchmarkTask) -> list[str]:
        lines = [f"Galaxy instance: {task.galaxy_instance}"]
        focused_hints = [hint for hint in [*task.tool_hints, *task.workflow_hints] if hint][:2]
        if focused_hints:
            lines.extend(f"Focus hint: {hint}" for hint in focused_hints)
        if "gtn_only" in {condition.value for condition in task.knowledge_requirements.conditions}:
            lines.append("Use the relevant GTN tutorial as guidance, then adapt it to the provided inputs.")
        if "iwc_only" in {condition.value for condition in task.knowledge_requirements.conditions}:
            lines.append("Use the relevant IWC workflow as guidance, then adapt it to the provided inputs.")
        if len(lines) == 1:
            lines.append("Select the appropriate Galaxy tool or workflow from the platform.")
        return lines

    def _resources_block(self, task: BenchmarkTask) -> str:
        return "\n".join(f"- {line}" for line in self._resource_lines(task))

    def _requirements_block(self, task: BenchmarkTask, tier: PromptTier) -> str:
        requirements = [
            "Use only the listed inputs and Galaxy-native resources relevant to the task.",
            "Adapt any retrieved tutorial or workflow to the current inputs instead of copying it blindly.",
            *self._tier_requirements[tier],
        ]
        return "\n".join(f"- {line}" for line in requirements)

    @staticmethod
    def _return_block(task: BenchmarkTask) -> str:
        if not task.expected_outputs:
            return "- Provide the final Galaxy result."
        return "\n".join(
            f"- `{field.field}`: {field.description}"
            for field in task.expected_outputs
        )
