from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

main_module = import_module("main")


def test_main_all_executes_protocol_in_documented_order(
    monkeypatch,
) -> None:
    """Smoke test do fluxo principal para garantir a ordem do protocolo."""

    executed_steps: list[str] = []

    monkeypatch.setattr(main_module, "load_config", lambda _path: {})

    step_mapping = [
        ("_run_inspect", "inspect"),
        ("_run_clean", "clean"),
        ("_run_validate", "validate"),
        ("_run_subset", "subset"),
        ("_run_segments", "segments"),
        ("_run_representations", "representations"),
        ("_run_melody_transformations", "melody_transform"),
        ("_run_harmony_transformations", "harmony_transform"),
        ("_run_rhythm_transformations", "rhythm_transform"),
        ("_run_combined_transformations", "combined_transform"),
        ("_run_validate_representations", "validate_representations"),
        ("_run_validate_transformations", "validate_transformations"),
        ("_run_compute_melody_metrics", "compute_melody_metrics"),
        ("_run_compute_harmony_metrics", "compute_harmony_metrics"),
        ("_run_compute_rhythm_metrics", "compute_rhythm_metrics"),
        ("_run_compute_global_metrics", "compute_global_metrics"),
        ("_run_validate_metrics", "validate_metrics"),
        ("_run_build_experiment_pairs", "build_experiment_pairs"),
        ("_run_similarity_experiment", "run_experiment"),
        ("_run_evaluate_robustness", "evaluate_robustness"),
        ("_run_evaluate_interpretability", "evaluate_interpretability"),
        ("_run_consolidate_results", "consolidate_results"),
        ("_run_generate_visualizations", "generate_visualizations"),
    ]

    for attribute_name, step_name in step_mapping:
        monkeypatch.setattr(
            main_module,
            attribute_name,
            lambda _config, current_step=step_name: executed_steps.append(current_step),
        )

    result = main_module.main(["all"])

    assert result == 0
    assert executed_steps == [step_name for _, step_name in step_mapping]
