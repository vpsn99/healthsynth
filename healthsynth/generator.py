from healthsynth.commercial.simulation import (
    CommercialSimulation,
    write_csv_outputs,
    write_duckdb_output,
)
from healthsynth.validation.checks import validate_datasets


def generate(
    module: str = "commercial_analytics",
    hcps: int = 1000,
    years: int = 3,
    scenario: str = "new_product_launch",
    output_dir: str = "output",
    seed: int = 42,
    config_path: str | None = None,
    output_format: str = "csv",
):
    if module != "commercial_analytics":
        raise ValueError("Only commercial_analytics is supported in v0.1")

    valid_output_formats = {"csv", "duckdb", "all"}
    if output_format not in valid_output_formats:
        raise ValueError(
            f"Invalid output_format '{output_format}'. Expected one of: csv, duckdb, all."
        )

    simulation = CommercialSimulation(
        hcps=hcps,
        years=years,
        scenario=scenario,
        seed=seed,
        config_path=config_path,
    )

    result = simulation.run()

    if output_format in ["csv", "all"]:
        write_csv_outputs(result=result, output_dir=output_dir)

    if output_format in ["duckdb", "all"]:
        write_duckdb_output(result=result, output_dir=output_dir)

    validate_datasets(
        datasets=result.as_dict(),
        years=years,
        output_dir=output_dir,
    )

    return result.as_dict()
