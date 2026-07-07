"""Ponto de entrada da aplicacao com comandos do experimento."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
import sys

import yaml

from experiment.clean_dataset import clean_dataset
from experiment.extract_representations import extract_representations
from experiment.extract_segments import extract_segments
from experiment.inspect_dataset import inspect_dataset
from experiment.select_subset import select_subset
from experiment.transform_combined import transform_combined
from experiment.transform_harmonies import transform_harmonies
from experiment.transform_melodies import transform_melodies
from experiment.transform_rhythms import transform_rhythms
from experiment.validate_representations import validate_representations
from experiment.validate_dataset import validate_dataset


DEFAULT_CONFIG_PATH = Path("config/default.yaml")


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
    _run_validate_representations(config)
    print()
    _run_validate(config)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
