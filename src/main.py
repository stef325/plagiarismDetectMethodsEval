from pathlib import Path

import yaml

from experiment.inspect_dataset import inspect_dataset
from experiment.validate_dataset import validate_dataset


def main() -> None:
    config = load_config(Path("config/default.yaml"))
    dataset_path = Path(config["dataset"]["path"])
    results_path = Path(config["paths"]["results"])
    inspection_report_path = (
        results_path / "inspect_dataset" / "pop909_inspection_report.md"
    )
    validation_report_path = (
        results_path / "validate_dataset" / "pop909_validation_report.md"
    )

    inspect_dataset(
        dataset_path=dataset_path,
        output_path=inspection_report_path,
    )
    print()
    validate_dataset(
        dataset_path=dataset_path,
        output_path=validation_report_path,
    )


def load_config(config_path: Path) -> dict:
    """Carrega a configuracao principal do projeto."""

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    main()
