from pathlib import Path

import yaml

from experiment.inspect_dataset import inspect_dataset


def main() -> None:
    config = load_config(Path("config/default.yaml"))
    dataset_path = Path(config["dataset"]["path"])
    results_path = Path(config["paths"]["results"])
    report_path = results_path / "inspect_dataset/pop909_inspection_report.md"
    inspect_dataset(dataset_path=dataset_path, output_path=report_path)


def load_config(config_path: Path) -> dict:
    """Carrega a configuracao principal do projeto."""

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    main()
