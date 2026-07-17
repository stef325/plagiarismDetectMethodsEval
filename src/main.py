"""Ponto de entrada da aplicacao com comandos do experimento."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import yaml


DEFAULT_CONFIG_PATH = Path("config/default.yaml")

inspect_dataset = import_module("experiment.01_inspect_dataset").inspect_dataset
clean_dataset = import_module("experiment.02_clean_dataset").clean_dataset
validate_dataset = import_module("experiment.03_validate_dataset").validate_dataset
select_subset = import_module("experiment.04_select_subset").select_subset
extract_segments = import_module("experiment.05_extract_segments").extract_segments
extract_representations = import_module(
    "experiment.06_extract_representations"
).extract_representations
transform_melodies = import_module(
    "experiment.07_transform_melodies"
).transform_melodies
transform_harmonies = import_module(
    "experiment.08_transform_harmonies"
).transform_harmonies
transform_rhythms = import_module(
    "experiment.09_transform_rhythms"
).transform_rhythms
transform_combined = import_module(
    "experiment.10_transform_combined"
).transform_combined
validate_representations = import_module(
    "experiment.11_validate_representations"
).validate_representations
validate_transformations = import_module(
    "experiment.12_validate_transformations"
).validate_transformations
compute_melody_metrics = import_module(
    "experiment.13_compute_melody_metrics"
).compute_melody_metrics
compute_harmony_metrics = import_module(
    "experiment.14_compute_harmony_metrics"
).compute_harmony_metrics
compute_rhythm_metrics = import_module(
    "experiment.15_compute_rhythm_metrics"
).compute_rhythm_metrics
compute_global_metrics = import_module(
    "experiment.16_compute_global_metrics"
).compute_global_metrics
validate_metrics = import_module("experiment.17_validate_metrics").validate_metrics
build_experiment_pairs = import_module(
    "experiment.18_build_experiment_pairs"
).build_experiment_pairs
run_similarity_experiment = import_module(
    "experiment.19_run_similarity_experiment"
).run_similarity_experiment
evaluate_robustness = import_module(
    "experiment.20_evaluate_robustness"
).evaluate_robustness
evaluate_interpretability = import_module(
    "experiment.21_evaluate_interpretability"
).evaluate_interpretability
consolidate_results = import_module(
    "experiment.22_consolidate_results"
).consolidate_results
generate_visualizations = import_module(
    "experiment.23_generate_visualizations"
).generate_visualizations


def main(argv: list[str] | None = None) -> int:
    """Executa o comando informado na linha de comando.

    Args:
        argv: Argumentos opcionais para facilitar testes.

    Returns:
        Codigo de saida do processo.
    """

    parser = _build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == "inspect":
        _run_inspect(config)
    elif args.command == "clean":
        _run_clean(config)
    elif args.command == "validate":
        _run_validate(config)
    elif args.command == "subset":
        _run_subset(config)
    elif args.command == "segments":
        _run_segments(config)
    elif args.command == "representations":
        _run_representations(config)
    elif args.command == "melody_transform":
        _run_melody_transformations(config)
    elif args.command == "harmony_transform":
        _run_harmony_transformations(config)
    elif args.command == "rhythm_transform":
        _run_rhythm_transformations(config)
    elif args.command == "combined_transform":
        _run_combined_transformations(config)
    elif args.command == "validate_representations":
        _run_validate_representations(config)
    elif args.command == "validate_transformations":
        _run_validate_transformations(config)
    elif args.command == "compute_melody_metrics":
        _run_compute_melody_metrics(config)
    elif args.command == "compute_harmony_metrics":
        _run_compute_harmony_metrics(config)
    elif args.command == "compute_rhythm_metrics":
        _run_compute_rhythm_metrics(config)
    elif args.command == "compute_global_metrics":
        _run_compute_global_metrics(config)
    elif args.command == "validate_metrics":
        _run_validate_metrics(config)
    elif args.command == "build_experiment_pairs":
        _run_build_experiment_pairs(config)
    elif args.command == "run_experiment":
        _run_similarity_experiment(config)
    elif args.command == "evaluate_robustness":
        _run_evaluate_robustness(config)
    elif args.command == "evaluate_interpretability":
        _run_evaluate_interpretability(config)
    elif args.command == "consolidate_results":
        _run_consolidate_results(config)
    elif args.command == "generate_visualizations":
        _run_generate_visualizations(config)
    elif args.command == "all":
        _run_all(config)
    else:
        parser.print_help()
        return 1

    return 0


def load_config(config_path: Path) -> dict:
    """Carrega a configuracao principal do projeto."""

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _build_parser() -> argparse.ArgumentParser:
    """Cria o parser de comandos da aplicacao."""

    parser = argparse.ArgumentParser(
        prog="python -m main",
        description="Executa etapas do experimento POP909.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Caminho do arquivo de configuracao YAML.",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser(
        "inspect",
        help="Executa apenas a inspeção estrutural do dataset.",
    )
    subparsers.add_parser(
        "clean",
        help="Executa apenas a limpeza do dataset.",
    )
    subparsers.add_parser(
        "validate",
        help="Executa apenas a validacao dos arquivos MIDI.",
    )
    subparsers.add_parser(
        "subset",
        help="Seleciona um subconjunto aleatorio do dataset processado.",
    )
    subparsers.add_parser(
        "segments",
        help="Extrai segmentos aleatorios das musicas processadas.",
    )
    subparsers.add_parser(
        "representations",
        help="Extrai melodia, harmonia e ritmo dos segmentos.",
    )
    subparsers.add_parser(
        "melody_transform",
        help="Aplica transformacoes melódicas nas representacoes extraidas.",
    )
    subparsers.add_parser(
        "harmony_transform",
        help="Aplica transformacoes harmonicas nas representacoes extraidas.",
    )
    subparsers.add_parser(
        "rhythm_transform",
        help="Aplica transformacoes ritmicas nas representacoes extraidas.",
    )
    subparsers.add_parser(
        "combined_transform",
        help="Aplica transformacoes combinadas nas representacoes extraidas.",
    )
    subparsers.add_parser(
        "validate_representations",
        help="Valida as representacoes musicais extraidas.",
    )
    subparsers.add_parser(
        "compute_melody_metrics",
        help="Calcula as metricas de similaridade melódica.",
    )
    subparsers.add_parser(
        "compute_harmony_metrics",
        help="Calcula as metricas de similaridade harmônica.",
    )
    subparsers.add_parser(
        "compute_rhythm_metrics",
        help="Calcula as metricas de similaridade rítmica.",
    )
    subparsers.add_parser(
        "validate_transformations",
        help="Valida as transformacoes geradas pelo experimento.",
    )
    subparsers.add_parser(
        "compute_global_metrics",
        help="Calcula a métrica global de similaridade.",
    )
    subparsers.add_parser(
        "validate_metrics",
        help="Executa a validação automatizada das métricas.",
    )
    subparsers.add_parser(
        "build_experiment_pairs",
        help="Forma os pares experimentais positivos e negativos.",
    )
    subparsers.add_parser(
        "run_experiment",
        help="Executa as métricas de similaridade sobre os pares experimentais.",
    )
    subparsers.add_parser(
        "evaluate_robustness",
        help="Avalia a robustez das métricas de similaridade.",
    )
    subparsers.add_parser(
        "evaluate_interpretability",
        help="Avalia a interpretabilidade das métricas de similaridade.",
    )
    subparsers.add_parser(
        "consolidate_results",
        help="Consolida os resultados já produzidos pelo experimento.",
    )
    subparsers.add_parser(
        "generate_visualizations",
        help="Gera as visualizacoes a partir dos resultados consolidados.",
    )
    subparsers.add_parser(
        "all",
        help="Executa todas as etapas do experimento em sequencia.",
    )

    return parser


def _run_inspect(config: dict) -> Path:
    """Executa o pipeline de inspecao."""

    dataset_path = Path(config["dataset"]["path"])
    results_path = Path(config["paths"]["results"])
    inspection_report_path = (
        results_path / "inspect_dataset" / "pop909_inspection_report.md"
    )

    return inspect_dataset(
        dataset_path=dataset_path,
        output_path=inspection_report_path,
    )


def _run_clean(config: dict) -> Path:
    """Executa o pipeline de limpeza."""

    dataset_path = Path(config["dataset"]["path"])
    processed_path = Path(config["paths"]["processed"])

    return clean_dataset(
        dataset_path=dataset_path,
        output_path=processed_path,
    )


def _run_validate(config: dict) -> Path:
    """Executa o pipeline de validacao."""

    dataset_path = Path(config["dataset"]["path"])
    results_path = Path(config["paths"]["results"])
    validation_report_path = (
        results_path / "validate_dataset" / "pop909_validation_report.md"
    )

    return validate_dataset(
        dataset_path=dataset_path,
        output_path=validation_report_path,
    )


def _run_subset(config: dict) -> Path:
    """Executa o pipeline de selecao de subconjunto."""

    processed_root = Path(config["paths"]["processed"])
    subset_config = config["subset"]

    return select_subset(
        source_path=processed_root / config["dataset"]["name"],
        output_path=Path(config["paths"]["subset"]),
        sample_size=subset_config["sample_size"],
        random_seed=subset_config["random_seed"],
    )


def _run_segments(config: dict) -> Path:
    """Executa o pipeline de extracao de segmentos."""

    segments_config = config["segments"]

    return extract_segments(
        source_path=Path(config["paths"]["subset"]),
        output_path=Path(config["paths"]["segments"]),
        measures_per_segment=segments_config["measures_per_segment"],
        segments_per_song=segments_config["segments_per_song"],
        random_seed=segments_config["random_seed"],
    )


def _run_representations(config: dict) -> Path:
    """Executa o pipeline de extracao das representacoes."""

    return extract_representations(
        source_path=Path(config["paths"]["segments"]),
        output_path=Path(config["paths"]["representations"]),
    )


def _run_melody_transformations(config: dict) -> Path:
    """Executa as transformacoes melodicas habilitadas."""

    melody_transform_config = config["melody_transformations"]
    return _run_transformations(
        source_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["transformations"]),
        transformation_section=melody_transform_config,
        transformation_runner=transform_melodies,
    )


def _run_harmony_transformations(config: dict) -> Path:
    """Executa as transformacoes harmonicas habilitadas."""

    harmony_transform_config = config["harmony_transformations"]
    return _run_transformations(
        source_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["transformations"]),
        transformation_section=harmony_transform_config,
        transformation_runner=transform_harmonies,
    )


def _run_rhythm_transformations(config: dict) -> Path:
    """Executa as transformacoes ritmicas habilitadas."""

    rhythm_transform_config = config["rhythm_transformations"]
    return _run_transformations(
        source_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["transformations"]),
        transformation_section=rhythm_transform_config,
        transformation_runner=transform_rhythms,
    )


def _run_combined_transformations(config: dict) -> Path:
    """Executa as transformacoes combinadas habilitadas."""

    combined_transform_config = config["combined_transformations"]
    return transform_combined(
        source_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["transformations"]),
        transformation_section=combined_transform_config,
    )


def _run_transformations(
    source_path: Path,
    output_path: Path,
    transformation_section: dict,
    transformation_runner: Callable[..., Path],
) -> Path:
    """Executa uma lista de transformacoes configuradas."""

    enabled_transformations = _get_enabled_transformations(transformation_section)
    random_seed = int(transformation_section["random_seed"])

    for transformation_name in enabled_transformations:
        parameters = dict(transformation_section.get(transformation_name, {}))
        transformation_runner(
            source_path=source_path,
            output_path=output_path,
            transformation_name=transformation_name,
            parameters=parameters,
            random_seed=random_seed,
        )

    return output_path


def _get_enabled_transformations(transformation_section: dict) -> list[str]:
    """Retorna as transformacoes habilitadas na configuracao."""

    enabled = transformation_section.get("enabled")
    if enabled is None:
        return [
            key
            for key in transformation_section
            if key not in {"random_seed", "enabled"}
        ]
    return list(enabled)


def _run_validate_representations(config: dict) -> Path:
    """Executa o pipeline de validacao das representacoes."""

    representations_root = Path(config["paths"]["representations"])
    segments_root = Path(config["paths"]["segments"])
    report_path = (
        Path(config["paths"]["results"]) / "validate_representations" / "representation_validation_report.md"
    )

    return validate_representations(
        representations_path=representations_root,
        segments_metadata_path=segments_root / "segments_metadata.csv",
        output_path=report_path,
    )


def _run_validate_transformations(config: dict) -> Path:
    """Executa o pipeline de validacao das transformacoes."""

    return validate_transformations(
        transformations_path=Path(config["paths"]["transformations"]),
        representations_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["transformation_validation"]),
    )


def _run_compute_melody_metrics(config: dict) -> Path:
    """Executa o pipeline de calculo das metricas melódicas."""

    return compute_melody_metrics(
        transformations_path=Path(config["paths"]["transformations"]),
        representations_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["metrics"]),
        interval_ngram_n=int(config["metrics"]["melody"]["interval_ngram_n"]),
    )


def _run_compute_harmony_metrics(config: dict) -> Path:
    """Executa o pipeline de calculo das metricas harmônicas."""

    return compute_harmony_metrics(
        transformations_path=Path(config["paths"]["transformations"]),
        representations_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["metrics"]),
        chord_ngram_n=int(config["metrics"]["harmony"]["chord_ngram_n"]),
    )


def _run_compute_rhythm_metrics(config: dict) -> Path:
    """Executa o pipeline de calculo das metricas rítmicas."""

    return compute_rhythm_metrics(
        transformations_path=Path(config["paths"]["transformations"]),
        representations_path=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["metrics"]),
        rhythm_ngram_n=int(config["metrics"]["rhythm"]["rhythm_ngram_n"]),
    )


def _run_compute_global_metrics(config: dict) -> Path:
    """Executa o pipeline de cálculo da métrica global."""

    return compute_global_metrics(
        metrics_path=Path(config["paths"]["metrics"]),
        output_path=Path(config["paths"]["results"]) / "compute_metrics",
        weights=dict(config["metrics"]["global"]["weights"]),
    )


def _run_validate_metrics(config: dict) -> Path:
    """Executa o pipeline de validação das métricas."""

    return validate_metrics(
        tests_path=Path("tests/metrics"),
        output_path=Path(config["paths"]["metrics"]),
    )


def _run_build_experiment_pairs(config: dict) -> Path:
    """Executa o pipeline de formação dos pares experimentais."""

    return build_experiment_pairs(
        representations_path=Path(config["paths"]["representations"]),
        transformations_path=Path(config["paths"]["transformations"]),
        output_path=Path(config["paths"]["experiment_pairs"]),
        random_seed=int(config["experiment"]["random_seed"]),
    )


def _run_similarity_experiment(config: dict) -> Path:
    """Executa o pipeline de similaridade sobre os pares experimentais."""

    return run_similarity_experiment(
        experiment_pairs_path=Path(config["paths"]["experiment_pairs"]),
        representations_root=Path(config["paths"]["representations"]),
        output_path=Path(config["paths"]["experiment_results"]),
        interval_ngram_n=int(config["metrics"]["melody"]["interval_ngram_n"]),
        chord_ngram_n=int(config["metrics"]["harmony"]["chord_ngram_n"]),
        rhythm_ngram_n=int(config["metrics"]["rhythm"]["rhythm_ngram_n"]),
        global_weights=dict(config["metrics"]["global"]["weights"]),
    )


def _run_evaluate_robustness(config: dict) -> Path:
    """Executa o pipeline de avaliacao da robustez das metricas."""

    return evaluate_robustness(
        experiment_pairs_path=Path(config["paths"]["experiment_pairs"]),
        similarity_results_path=Path(config["paths"]["experiment_results"]) / "similarity_results.csv",
        output_path=Path(config["paths"]["results"]) / "evaluation",
        similarity_threshold=float(config["evaluation"]["similarity_threshold"]),
    )


def _run_evaluate_interpretability(config: dict) -> Path:
    """Executa o pipeline de avaliacao da interpretabilidade."""

    return evaluate_interpretability(
        experiment_pairs_path=Path(config["paths"]["experiment_pairs"]),
        similarity_results_path=Path(config["paths"]["experiment_results"]) / "similarity_results.csv",
        transformations_root=Path(config["paths"]["transformations"]),
        output_path=Path(config["paths"]["results"]) / "evaluation" / "interpretability",
    )


def _run_consolidate_results(config: dict) -> Path:
    """Executa o pipeline de consolidacao dos resultados."""

    return consolidate_results(
        similarity_results_path=Path(config["paths"]["experiment_results"]) / "similarity_results.csv",
        robustness_results_path=Path(config["paths"]["results"]) / "evaluation" / "robustness_metrics.csv",
        interpretability_results_path=Path(config["paths"]["results"]) / "evaluation" / "interpretability" / "interpretability_results.csv",
        output_path=Path(config["paths"]["results"]) / "consolidated",
    )


def _run_generate_visualizations(config: dict) -> Path:
    """Executa o pipeline de geracao das visualizacoes."""

    return generate_visualizations(
        consolidated_root=Path(config["paths"]["results"]) / "consolidated",
        output_path=Path(config["paths"]["results"]) / "figures",
    )


def _run_all(config: dict) -> None:
    """Executa todas as etapas do experimento."""

    _run_inspect(config)
    print()
    _run_clean(config)
    print()
    _run_subset(config)
    print()
    _run_segments(config)
    print()
    _run_representations(config)
    print()
    _run_melody_transformations(config)
    print()
    _run_harmony_transformations(config)
    print()
    _run_rhythm_transformations(config)
    print()
    _run_combined_transformations(config)
    print()
    _run_validate_transformations(config)
    print()
    _run_compute_melody_metrics(config)
    print()
    _run_compute_harmony_metrics(config)
    print()
    _run_compute_rhythm_metrics(config)
    print()
    _run_compute_global_metrics(config)
    print()
    _run_build_experiment_pairs(config)
    print()
    _run_similarity_experiment(config)
    print()
    _run_evaluate_robustness(config)
    print()
    _run_evaluate_interpretability(config)
    print()
    _run_consolidate_results(config)
    print()
    _run_generate_visualizations(config)
    print()
    _run_validate_metrics(config)
    print()
    _run_validate_representations(config)
    print()
    _run_validate(config)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
