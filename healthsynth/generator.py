import time
from pathlib import Path

from healthsynth.commercial.simulation import (
    CommercialSimulation,
    write_csv_outputs,
    write_duckdb_output,
)
from healthsynth.config.loader import ConfigLoader
from healthsynth.validation.checks import validate_datasets


def generate(
    module: str = "commercial_analytics",
    hcps: int | None = None,
    years: int | None = None,
    scenario: str | None = None,
    output_dir: str = "output",
    seed: int | None = None,
    config_path: str | None = None,
    output_format: str | None = None,
):
    if module != "commercial_analytics":
        raise ValueError("Only commercial_analytics is supported in v0.1")

    config = ConfigLoader.load(config_path)
    generation_config = config.get("generation", {})

    resolved_hcps = hcps if hcps is not None else generation_config.get("hcps", 1000)
    resolved_years = years if years is not None else generation_config.get("years", 3)
    resolved_seed = seed if seed is not None else generation_config.get("seed", 42)
    resolved_scenario = (
        scenario
        if scenario is not None
        else generation_config.get("scenario", "new_product_launch")
    )
    resolved_output_format = (
        output_format
        if output_format is not None
        else generation_config.get("output_format", "csv")
    )

    valid_output_formats = {"csv", "duckdb", "all"}
    if resolved_output_format not in valid_output_formats:
        raise ValueError(
            f"Invalid output_format '{resolved_output_format}'. Expected one of: csv, duckdb, all."
        )

    timings = {}

    simulation = CommercialSimulation(
        hcps=resolved_hcps,
        years=resolved_years,
        scenario=resolved_scenario,
        seed=resolved_seed,
        config_path=config_path,
    )

    start = time.perf_counter()
    result = simulation.run()
    timings["simulation"] = time.perf_counter() - start

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    if resolved_output_format == "csv":
        duckdb_file = output_path / "healthsynth.duckdb"
        if duckdb_file.exists():
            duckdb_file.unlink()

    if resolved_output_format == "duckdb":
        for csv_file in output_path.glob("*.csv"):
            csv_file.unlink()

    timings["cleanup"] = time.perf_counter() - start

    if resolved_output_format in ["csv", "all"]:
        start = time.perf_counter()
        write_csv_outputs(result=result, output_dir=output_dir)
        timings["csv_export"] = time.perf_counter() - start

    if resolved_output_format in ["duckdb", "all"]:
        start = time.perf_counter()
        write_duckdb_output(result=result, output_dir=output_dir)
        timings["duckdb_export"] = time.perf_counter() - start

    start = time.perf_counter()
    validate_datasets(
        datasets=result.as_dict(),
        years=resolved_years,
        output_dir=output_dir,
    )
    timings["validation"] = time.perf_counter() - start

    timings["total"] = sum(timings.values())

    datasets = result.as_dict()
    datasets["_timings"] = timings

    return datasets
