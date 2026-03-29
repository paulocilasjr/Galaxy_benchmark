from __future__ import annotations

from galaxy_benchmark.application.scoring.scorers import ScoreAggregator


def test_score_aggregator_uses_blueprint_component_weights() -> None:
    scorecard = ScoreAggregator().build(
        outcome=(1.0, {"outcome_field_match_score": 1.0}),
        process=(0.5, {"process_parameter_correctness": 0.5}),
        robustness=(0.25, {"robustness_repeat_consistency": 0.25}),
    )

    assert scorecard.component_weights == {
        "outcome": 0.5,
        "process": 0.3,
        "robustness": 0.2,
    }
    assert scorecard.total_score == 0.7
