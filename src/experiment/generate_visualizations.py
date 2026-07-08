"""Pipeline para geracao das visualizacoes do experimento."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
import time
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


METRIC_COLUMNS = {
    "Interval N-Gram Similarity": "interval_ngram_similarity",
    "LCS": "lcs_similarity",
    "Edit Distance": "edit_distance_similarity",
    "Chord N-Gram Similarity": "chord_ngram_similarity",
    "Harmonic Edit Distance": "harmonic_edit_distance",
    "Pitch Class Similarity": "pitch_class_similarity",
    "Rhythm N-Gram Similarity": "rhythm_ngram_similarity",
    "IOI Similarity": "ioi_similarity",
    "Rhythmic Edit Distance": "rhythmic_edit_distance",
    "Métrica Global": "score_global",
}

FAMILY_LABELS = {
    "score_melody": "Melodia",
    "score_harmony": "Harmonia",
    "score_rhythm": "Ritmo",
    "score_global": "Global",
}


@dataclass(frozen=True)
class FigureRecord:
    """Representa uma figura gerada pelo pipeline."""

    name: str
    description: str
    category: str
    png_path: Path
    svg_path: Path | None = None


@dataclass(frozen=True)
class VisualizationSummary:
    """Resumo da geracao das visualizacoes."""

    consolidated_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    figures_generated: int
    fingerprint: str


def generate_visualizations(
    consolidated_root: str | Path = "data/results/consolidated",
    output_path: str | Path = "data/results/figures",
    generate_svg: bool = True,
) -> Path:
    """Gera visualizacoes a partir dos resultados consolidados."""

    consolidated_path = Path(consolidated_root)
    output_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    similarity_path = consolidated_path / "consolidated_similarity.csv"
    robustness_path = consolidated_path / "consolidated_robustness.csv"
    interpretability_path = consolidated_path / "consolidated_interpretability.csv"
    experiment_summary_path = consolidated_path / "experiment_summary.csv"
    statistics_summary_path = consolidated_path / "statistics_summary.csv"

    for path, label in (
        (similarity_path, "similaridade consolidada"),
        (robustness_path, "robustez consolidada"),
        (interpretability_path, "interpretabilidade consolidada"),
        (experiment_summary_path, "resumo por experimento"),
        (statistics_summary_path, "estatisticas consolidadas"),
    ):
        if not path.is_file():
            raise FileNotFoundError(f"Arquivo de {label} nao encontrado: {path}")

    output_root.mkdir(parents=True, exist_ok=True)
    for directory_name in ("distributions", "comparisons", "heatmaps", "boxplots"):
        (output_root / directory_name).mkdir(parents=True, exist_ok=True)

    figures_index_path = output_root / "figures_index.csv"
    report_path = output_root / "visualizations.md"
    cache_path = output_root / "visualizations_cache.json"

    fingerprint = _compute_fingerprint(
        [
            similarity_path,
            robustness_path,
            interpretability_path,
            experiment_summary_path,
            statistics_summary_path,
        ]
    )
    if _is_cache_valid(cache_path, figures_index_path, report_path, fingerprint):
        _print_cache_summary(cache_path, output_root)
        return output_root

    similarity_df = pd.read_csv(similarity_path)
    robustness_df = pd.read_csv(robustness_path)
    interpretability_df = pd.read_csv(interpretability_path)
    experiment_summary_df = pd.read_csv(experiment_summary_path)

    _validate_similarity_columns(similarity_df)

    sns.set_theme(style="whitegrid", context="talk")
    figure_records: list[FigureRecord] = []

    figure_records.extend(
        _generate_distribution_figures(
            similarity_df=similarity_df,
            output_root=output_root / "distributions",
            generate_svg=generate_svg,
        )
    )
    figure_records.extend(
        _generate_comparison_figures(
            similarity_df=similarity_df,
            experiment_summary_df=experiment_summary_df,
            output_root=output_root / "comparisons",
            generate_svg=generate_svg,
        )
    )
    figure_records.extend(
        _generate_heatmaps(
            similarity_df=similarity_df,
            interpretability_df=interpretability_df,
            output_root=output_root / "heatmaps",
            generate_svg=generate_svg,
        )
    )
    figure_records.extend(
        _generate_boxplots(
            similarity_df=similarity_df,
            output_root=output_root / "boxplots",
            generate_svg=generate_svg,
        )
    )

    _write_figures_index(figures_index_path, figure_records)
    _write_report(report_path, figure_records, output_root)
    _write_cache(cache_path, fingerprint, figure_records, report_path)

    summary = VisualizationSummary(
        consolidated_path=consolidated_path,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        figures_generated=len(figure_records),
        fingerprint=fingerprint,
    )
    _print_summary(summary, report_path)
    return output_root


def _validate_similarity_columns(similarity_df: pd.DataFrame) -> None:
    """Valida se a consolidacao contem as colunas necessarias."""

    required_columns = {
        "pair_id",
        "pair_type",
        "transformation",
        "score_melody",
        "score_harmony",
        "score_rhythm",
        "score_global",
        "comparison_representation",
        "experiment_category",
        *METRIC_COLUMNS.values(),
    }
    missing_columns = sorted(required_columns - set(similarity_df.columns))
    if missing_columns:
        raise ValueError(
            "Os resultados consolidados nao possuem todas as colunas necessarias "
            "para as visualizacoes. Execute novamente o pipeline consolidate_results. "
            f"Colunas ausentes: {', '.join(missing_columns)}"
        )


def _generate_distribution_figures(
    similarity_df: pd.DataFrame,
    output_root: Path,
    generate_svg: bool,
) -> list[FigureRecord]:
    """Gera histogramas de distribuicao para todas as metricas."""

    figure_records: list[FigureRecord] = []
    for metric_name, column_name in METRIC_COLUMNS.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(
            data=similarity_df,
            x=column_name,
            hue="pair_type",
            kde=True,
            bins=30,
            stat="density",
            common_norm=False,
            ax=ax,
        )
        ax.set_title(f"Distribuicao de {metric_name}")
        ax.set_xlabel(metric_name)
        ax.set_ylabel("Densidade")
        figure_records.append(
            _save_figure(
                fig=fig,
                output_root=output_root,
                file_stem=f"distribution_{_slugify(column_name)}",
                category="distributions",
                description=f"Distribuicao da metrica {metric_name} por tipo de par.",
                generate_svg=generate_svg,
            )
        )
    return figure_records


def _generate_comparison_figures(
    similarity_df: pd.DataFrame,
    experiment_summary_df: pd.DataFrame,
    output_root: Path,
    generate_svg: bool,
) -> list[FigureRecord]:
    """Gera graficos comparativos entre metricas e transformacoes."""

    figure_records: list[FigureRecord] = []

    family_df = similarity_df.melt(
        id_vars=["pair_id", "pair_type", "experiment_category"],
        value_vars=["score_melody", "score_harmony", "score_rhythm"],
        var_name="family",
        value_name="score",
    )
    family_df["family"] = family_df["family"].map(FAMILY_LABELS)
    experiment_df = similarity_df[similarity_df["experiment_category"] != "Outros"].copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=family_df, x="family", y="score", ax=ax)
    ax.set_title("Comparacao entre metricas melodicas, harmonicas e ritmicas")
    ax.set_xlabel("Familia de metricas")
    ax.set_ylabel("Score")
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="comparison_metric_families",
            category="comparisons",
            description="Comparacao entre os scores agregados de melodia, harmonia e ritmo.",
            generate_svg=generate_svg,
        )
    )

    global_comparison_df = similarity_df.melt(
        id_vars=["pair_id", "pair_type", "experiment_category"],
        value_vars=["score_melody", "score_harmony", "score_rhythm", "score_global"],
        var_name="metric_group",
        value_name="score",
    )
    global_comparison_df["metric_group"] = global_comparison_df["metric_group"].map(
        FAMILY_LABELS
    )
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.violinplot(data=global_comparison_df, x="metric_group", y="score", inner="quart", ax=ax)
    ax.set_title("Metricas individuais versus metrica global")
    ax.set_xlabel("Grupo de metricas")
    ax.set_ylabel("Score")
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="comparison_individual_vs_global",
            category="comparisons",
            description="Comparacao das metricas individuais com a metrica global.",
            generate_svg=generate_svg,
        )
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=experiment_summary_df[experiment_summary_df["experiment"] != "Outros"],
        x="experiment",
        y="mean_global_score",
        ax=ax,
    )
    ax.set_title("Desempenho medio da metrica global por tipo de transformacao")
    ax.set_xlabel("Experimento")
    ax.set_ylabel("Score global medio")
    ax.tick_params(axis="x", rotation=20)
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="comparison_global_by_experiment",
            category="comparisons",
            description="Comparacao do score global medio por tipo de transformacao.",
            generate_svg=generate_svg,
        )
    )

    return figure_records


def _generate_heatmaps(
    similarity_df: pd.DataFrame,
    interpretability_df: pd.DataFrame,
    output_root: Path,
    generate_svg: bool,
) -> list[FigureRecord]:
    """Gera heatmaps do experimento."""

    figure_records: list[FigureRecord] = []
    experiment_df = similarity_df[similarity_df["experiment_category"] != "Outros"].copy()

    correlation_columns = list(METRIC_COLUMNS.values())
    correlation_df = similarity_df[correlation_columns].astype(float).corr()
    fig, ax = plt.subplots(figsize=(12, 9))
    sns.heatmap(correlation_df, cmap="viridis", annot=False, square=True, ax=ax)
    ax.set_title("Correlacao entre metricas de similaridade")
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="heatmap_metric_correlation",
            category="heatmaps",
            description="Heatmap de correlacao entre todas as metricas de similaridade.",
            generate_svg=generate_svg,
        )
    )

    performance_by_experiment = (
        experiment_df.groupby("experiment_category")[
            ["score_melody", "score_harmony", "score_rhythm", "score_global"]
        ]
        .mean(numeric_only=True)
        .astype(float)
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(performance_by_experiment, cmap="mako", annot=True, fmt=".3f", ax=ax)
    ax.set_title("Desempenho medio por tipo de transformacao")
    ax.set_xlabel("Metrica")
    ax.set_ylabel("Experimento")
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="heatmap_performance_by_transformation",
            category="heatmaps",
            description="Heatmap do desempenho medio por tipo de transformacao.",
            generate_svg=generate_svg,
        )
    )

    component_heatmap_df = (
        interpretability_df.groupby("component_transformed")[
            ["score_melody", "score_harmony", "score_rhythm", "score_global"]
        ]
        .mean(numeric_only=True)
        .astype(float)
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(component_heatmap_df, cmap="crest", annot=True, fmt=".3f", ax=ax)
    ax.set_title("Desempenho medio por componente musical")
    ax.set_xlabel("Metrica")
    ax.set_ylabel("Componente")
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="heatmap_performance_by_component",
            category="heatmaps",
            description="Heatmap do desempenho medio por componente musical transformado.",
            generate_svg=generate_svg,
        )
    )

    return figure_records


def _generate_boxplots(
    similarity_df: pd.DataFrame,
    output_root: Path,
    generate_svg: bool,
) -> list[FigureRecord]:
    """Gera boxplots para metricas e comparacoes."""

    figure_records: list[FigureRecord] = []
    experiment_df = similarity_df[similarity_df["experiment_category"] != "Outros"].copy()

    metric_df = similarity_df.melt(
        id_vars=["pair_id", "pair_type", "experiment_category"],
        value_vars=list(METRIC_COLUMNS.values()),
        var_name="metric",
        value_name="score",
    )
    fig, ax = plt.subplots(figsize=(16, 7))
    sns.boxplot(data=metric_df, x="metric", y="score", ax=ax)
    ax.set_title("Boxplots das metricas individuais e da metrica global")
    ax.set_xlabel("Metrica")
    ax.set_ylabel("Score")
    ax.tick_params(axis="x", rotation=30)
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="boxplot_all_metrics",
            category="boxplots",
            description="Boxplots de todas as metricas individuais e da metrica global.",
            generate_svg=generate_svg,
        )
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(
        data=experiment_df,
        x="experiment_category",
        y="score_global",
        ax=ax,
    )
    ax.set_title("Boxplot do score global por tipo de transformacao")
    ax.set_xlabel("Experimento")
    ax.set_ylabel("Score global")
    ax.tick_params(axis="x", rotation=20)
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="boxplot_global_by_transformation",
            category="boxplots",
            description="Boxplot do score global por tipo de transformacao.",
            generate_svg=generate_svg,
        )
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=similarity_df, x="pair_type", y="score_global", ax=ax)
    ax.set_title("Boxplot da metrica global por tipo de par")
    ax.set_xlabel("Tipo de par")
    ax.set_ylabel("Score global")
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="boxplot_global_by_pair_type",
            category="boxplots",
            description="Boxplot do score global comparando pares positivos e negativos.",
            generate_svg=generate_svg,
        )
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=experiment_df, x="transformation", y="score_global", ax=ax)
    ax.set_title("Boxplot do score global por transformacao")
    ax.set_xlabel("Transformacao")
    ax.set_ylabel("Score global")
    ax.tick_params(axis="x", rotation=45)
    figure_records.append(
        _save_figure(
            fig=fig,
            output_root=output_root,
            file_stem="boxplot_global_by_transformation_name",
            category="boxplots",
            description="Boxplot do score global por transformacao especifica.",
            generate_svg=generate_svg,
        )
    )

    return figure_records


def _save_figure(
    fig: plt.Figure,
    output_root: Path,
    file_stem: str,
    category: str,
    description: str,
    generate_svg: bool,
) -> FigureRecord:
    """Salva uma figura em PNG e opcionalmente em SVG."""

    png_path = output_root / f"{file_stem}.png"
    fig.tight_layout()
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    svg_path: Path | None = None
    if generate_svg:
        svg_path = output_root / f"{file_stem}.svg"
        fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    return FigureRecord(
        name=file_stem,
        description=description,
        category=category,
        png_path=png_path,
        svg_path=svg_path,
    )


def _write_figures_index(index_path: Path, records: list[FigureRecord]) -> None:
    """Escreve o indice das figuras geradas."""

    with index_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["name", "description", "category", "png_file", "svg_file"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "name": record.name,
                    "description": record.description,
                    "category": record.category,
                    "png_file": record.png_path.as_posix(),
                    "svg_file": record.svg_path.as_posix() if record.svg_path else "",
                }
            )


def _write_report(report_path: Path, records: list[FigureRecord], output_root: Path) -> None:
    """Escreve o relatorio Markdown das visualizacoes."""

    lines = [
        "# Relatório de Visualizações",
        "",
        f"Localização base: {output_root.as_posix()}",
        "",
        "## Figuras geradas",
        "",
        "| Nome | Categoria | Descrição | Arquivo PNG | Arquivo SVG |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    record.name,
                    record.category,
                    record.description.replace("|", "\\|"),
                    record.png_path.as_posix(),
                    record.svg_path.as_posix() if record.svg_path else "-",
                ]
            )
            + " |"
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_cache(
    cache_path: Path,
    fingerprint: str,
    records: list[FigureRecord],
    report_path: Path,
) -> None:
    """Escreve o cache das visualizacoes."""

    cache_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "figures_generated": len(records),
                "report_path": report_path.as_posix(),
                "figures": [
                    {
                        "name": record.name,
                        "category": record.category,
                        "png_path": record.png_path.as_posix(),
                        "svg_path": record.svg_path.as_posix() if record.svg_path else "",
                    }
                    for record in records
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _is_cache_valid(
    cache_path: Path,
    figures_index_path: Path,
    report_path: Path,
    fingerprint: str,
) -> bool:
    """Verifica se o cache ainda e valido."""

    if not cache_path.is_file() or not figures_index_path.is_file() or not report_path.is_file():
        return False
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    if payload.get("fingerprint") != fingerprint:
        return False
    for figure in payload.get("figures", []):
        png_path = Path(figure.get("png_path", ""))
        if not png_path.is_file():
            return False
        svg_value = figure.get("svg_path", "")
        if svg_value and not Path(svg_value).is_file():
            return False
    return True


def _print_cache_summary(cache_path: Path, output_root: Path) -> None:
    """Exibe um resumo quando as figuras sao reutilizadas."""

    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    print("Visualizações reutilizadas a partir do cache.")
    print(f"Saída: {output_root.as_posix()}")
    print(f"Figuras geradas: {payload.get('figures_generated', 0)}")


def _print_summary(summary: VisualizationSummary, report_path: Path) -> None:
    """Exibe um resumo amigavel da geracao de figuras."""

    print("Geração das visualizações concluída.")
    print(f"Figuras geradas: {summary.figures_generated}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatório gerado em: {report_path.as_posix()}")


def _compute_fingerprint(paths: list[Path]) -> str:
    """Gera uma assinatura estavel dos arquivos consolidados."""

    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


def _slugify(value: str) -> str:
    """Normaliza um texto para uso em nome de arquivo."""

    return (
        value.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )
