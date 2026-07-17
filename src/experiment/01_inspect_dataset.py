"""Pipeline da etapa de inspecao estrutural do dataset."""

from __future__ import annotations

from pathlib import Path

from preprocessing.dataset.pop909_inspector import POP909Inspector


def inspect_dataset(dataset_path: str | Path, output_path: str | Path) -> Path:
    """Executa a inspecao estrutural do dataset e gera o relatorio."""

    dataset_root = Path(dataset_path)
    report_path = Path(output_path)
    inspector = POP909Inspector(dataset_root)

    print("Iniciando a inspecao estrutural do dataset POP909...")
    inspector.print_summary()
    inspector.export_report(report_path)
    print()
    print(f"Relatorio de inspecao gerado em: {report_path.as_posix()}")

    return report_path
