"""Pipeline para validação das métricas do projeto."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import time
from typing import Any

import pytest


@dataclass(frozen=True)
class MetricValidationRecord:
    """Representa o resultado de um teste de métrica."""

    metric: str
    test_case: str
    obtained_result: str
    expected_result: str
    status: str
    error_message: str


@dataclass(frozen=True)
class MetricValidationSummary:
    """Resumo consolidado da validação das métricas."""

    tests_root: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    total_tests: int
    tests_passed: int
    tests_failed: int
    success_rate: float
    fingerprint: str


class MetricValidationCollector:
    """Coleta os resultados de cada teste executado pelo pytest."""

    def __init__(self) -> None:
        self.records: list[MetricValidationRecord] = []

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo[Any]):
        """Coleta os resultados de execução de cada teste."""

        outcome = yield
        report = outcome.get_result()

        if report.when != "call":
            return

        marker = item.get_closest_marker("metric_case")
        if marker is None:
            return

        properties = dict(report.user_properties)
        metric_value = properties.get("metric_value", "")
        expected_result = str(marker.kwargs.get("expected", ""))
        metric_name = str(marker.kwargs.get("metric", item.name))
        test_case = str(marker.kwargs.get("case", item.name))
        status = "PASS" if report.passed else "FAIL"
        error_message = "" if report.passed else report.longreprtext
        obtained_result = metric_value if metric_value else status

        self.records.append(
            MetricValidationRecord(
                metric=metric_name,
                test_case=test_case,
                obtained_result=obtained_result,
                expected_result=expected_result,
                status=status,
                error_message=error_message,
            )
        )


def validate_metrics(
    tests_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Executa a suíte de validação das métricas com pytest."""

    tests_root = Path(tests_path)
    output_root = Path(output_path) / "validation"
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not tests_root.is_dir():
        raise FileNotFoundError(f"Diretório de testes não encontrado: {tests_root}")

    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / "metrics_validation_report.md"
    cache_path = output_root / "metrics_validation_cache.json"

    fingerprint = _compute_fingerprint(
        [
            Path("src/metrics"),
            tests_root,
            Path("src/preprocessing/representation"),
        ]
    )

    if report_path.is_file() and cache_path.is_file():
        cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached_payload.get("fingerprint") == fingerprint:
            _print_summary_from_cache(report_path, cached_payload)
            return output_root

    print("Iniciando a validação das métricas com pytest...")

    collector = MetricValidationCollector()
    pytest_args = [
        str(tests_root),
        "--disable-warnings",
        "-q",
    ]
    exit_code = pytest.main(pytest_args, plugins=[collector])

    total_tests = len(collector.records)
    tests_passed = sum(1 for record in collector.records if record.status == "PASS")
    tests_failed = sum(1 for record in collector.records if record.status == "FAIL")
    success_rate = (tests_passed / total_tests * 100.0) if total_tests else 0.0

    summary = MetricValidationSummary(
        tests_root=tests_root,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        total_tests=total_tests,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        success_rate=success_rate,
        fingerprint=fingerprint,
    )

    _write_report(report_path, summary, collector.records)
    cache_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "total_tests": total_tests,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "success_rate": success_rate,
                "records": [record.__dict__ for record in collector.records],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    _print_summary(summary, report_path, exit_code)
    return output_root


def _compute_fingerprint(paths: list[Path]) -> str:
    """Gera uma assinatura estável do conteúdo dos arquivos relevantes."""

    digest = hashlib.sha256()
    for root in paths:
        if not root.exists():
            continue
        for file_path in sorted(root.rglob("*.py")):
            digest.update(file_path.as_posix().encode("utf-8"))
            digest.update(file_path.read_bytes())
    return digest.hexdigest()


def _write_report(
    report_path: Path,
    summary: MetricValidationSummary,
    records: list[MetricValidationRecord],
) -> None:
    """Escreve o relatório Markdown consolidado."""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Relatório de Validação das Métricas",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Resumo",
        "",
        f"- Total de testes: {summary.total_tests}",
        f"- Testes aprovados: {summary.tests_passed}",
        f"- Testes reprovados: {summary.tests_failed}",
        f"- Percentual de sucesso: {summary.success_rate:.2f}%",
        "",
        "## Resultados",
        "",
        "| Métrica testada | Caso de teste | Resultado obtido | Resultado esperado | Status | Mensagem de erro |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(record.metric),
                    _escape_markdown(record.test_case),
                    _escape_markdown(record.obtained_result),
                    _escape_markdown(record.expected_result),
                    _escape_markdown(record.status),
                    _escape_markdown(record.error_message or "-"),
                ]
            )
            + " |"
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_summary(
    summary: MetricValidationSummary,
    report_path: Path,
    exit_code: int,
) -> None:
    """Exibe um resumo amigável da validação."""

    print("Validação das métricas concluída.")
    print(f"Testes raiz: {summary.tests_root.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Total de testes: {summary.total_tests}")
    print(f"Testes aprovados: {summary.tests_passed}")
    print(f"Testes reprovados: {summary.tests_failed}")
    print(f"Percentual de sucesso: {summary.success_rate:.2f}%")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatório gerado em: {report_path.as_posix()}")
    print(f"Saída do pytest: {exit_code}")


def _print_summary_from_cache(report_path: Path, cached_payload: dict[str, Any]) -> None:
    """Exibe um resumo quando a validação reutiliza o cache."""

    print("Validação das métricas reutilizada a partir do cache.")
    print(f"Relatório gerado em: {report_path.as_posix()}")
    print(f"Total de testes: {cached_payload.get('total_tests', 0)}")
    print(f"Testes aprovados: {cached_payload.get('tests_passed', 0)}")
    print(f"Testes reprovados: {cached_payload.get('tests_failed', 0)}")
    print(f"Percentual de sucesso: {cached_payload.get('success_rate', 0.0):.2f}%")


def _escape_markdown(value: str) -> str:
    """Escapa caracteres especiais para tabelas Markdown."""

    return value.replace("|", "\\|").replace("\n", " ")

