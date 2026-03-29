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
        normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in content.strip().splitlines()]
        return "\n".join(line for line in normalized_lines if line)


class PromptTemplateRepository:
    """Filesystem-backed prompt template loader with deterministic fallbacks."""

    _defaults = {
        PromptFormat.PROSE: (
            "{description} Use {inputs}. {tier_instruction} "
            "Prefer this guidance when available: {hints}. "
            "Return structured outputs for {outputs}."
        ),
        PromptFormat.BULLETS: (
            "Task: {description}\n"
            "- Inputs: {inputs}\n"
            "- Guidance: {hints}\n"
            "- Expected outputs: {outputs}\n"
            "- Tier behavior: {tier_instruction}"
        ),
        PromptFormat.STRUCTURED: (
            "Task ID: {task_id}\n"
            "Prompt Tier: {tier}\n"
            "Task Family: {task_family}\n"
            "Goal: {description}\n"
            "Inputs: {inputs}\n"
            "Hints: {hints}\n"
            "Expected Outputs: {outputs}\n"
            "Instructions: {tier_instruction}"
        ),
        PromptFormat.JSON_LIKE: (
            "{{"
            '"task_id": "{task_id}", '
            '"tier": "{tier}", '
            '"task_family": "{task_family}", '
            '"objective": "{description}", '
            '"inputs": "{inputs}", '
            '"hints": "{hints}", '
            '"required_outputs": "{outputs}", '
            '"tier_instruction": "{tier_instruction}"'
            "}}"
        ),
    }

    def __init__(self, root: Path | str = Path("benchmark/prompts/templates")) -> None:
        self.root = Path(root)

    def load(self, prompt_format: PromptFormat) -> str:
        template_path = self.root / f"{prompt_format.value}.txt"
        if template_path.exists():
            return template_path.read_text()
        return self._defaults[prompt_format]


class PromptVariantGenerator:
    """Generate prompt variants across tiers and formats."""

    _tier_instruction = {
        PromptTier.NOVICE: "Be explicit about each step and the expected deliverables.",
        PromptTier.INTERMEDIATE: "Balance guidance with room for informed defaults.",
        PromptTier.EXPERT: "Use concise task language and assume domain familiarity.",
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
        inputs = ", ".join(asset.name for asset in task.input_assets) or "the provided inputs"
        outputs = ", ".join(task.normalized_output_field_names())
        hints = ", ".join(task.tool_hints or task.workflow_hints) or "discover the appropriate Galaxy tools or workflows"
        tier_instruction = self._tier_instruction[tier]
        template = self._templates.load(prompt_format)
        return template.format(
            task_id=task.task_id,
            tier=tier.value,
            task_family=task.task_family.value,
            description=task.description,
            inputs=inputs,
            hints=hints,
            outputs=outputs,
            tier_instruction=tier_instruction,
        )
