import time

import typer
from rich.console import Console

from healthsynth import __version__
from healthsynth.generator import generate as run_generation

app = typer.Typer(
    name="healthsynth",
    help="Synthetic pharma commercial analytics data generator.",
)

console = Console()


@app.command()
def demo():
    """
    Generate a demo commercial analytics environment.
    """
    console.print("[bold green]Generating HealthSynth demo dataset[/bold green]")
    start_time = time.perf_counter()

    datasets = run_generation(
        module="commercial_analytics",
        hcps=1000,
        years=3,
        scenario="new_product_launch",
        output_dir="demo_output",
        seed=42,
        config_path="configs/demo.yaml",
        output_format="all",
    )
    elapsed_seconds = time.perf_counter() - start_time

    console.print("[bold green]Demo generation complete[/bold green]")
    if "market" in datasets:
        console.print(f"Created {len(datasets['market'])} market records")
    console.print(f"Created {len(datasets['hcp_master'])} HCP records")
    console.print(f"Created {len(datasets['product'])} product records")
    if "market_share" in datasets:
        console.print(f"Created {len(datasets['market_share'])} market share records")
    if "promotion_effect" in datasets:
        console.print(f"Created {len(datasets['promotion_effect'])} promotion effect records")
    console.print(f"Created {len(datasets['call_activity'])} activity records")
    console.print(f"Created {len(datasets['prescriptions'])} prescription records")
    if "market_demand" in datasets:
        console.print(f"Created {len(datasets['market_demand'])} market demand records")

    console.print("Output written to: demo_output")
    console.print(f"Generation time: {elapsed_seconds:.2f} seconds")
    timings = datasets.get("_timings", {})

    if timings:
        console.print("")
        console.print("[bold]Timing breakdown[/bold]")
        for step, seconds in timings.items():
            console.print(f"- {step}: {seconds:.2f}s")


@app.command()
def version():
    console.print(f"HealthSynth version {__version__}")


@app.callback()
def main():
    """
    HealthSynth CLI.
    """
    pass


@app.command()
def generate(
    module: str = typer.Option("commercial_analytics", help="Module to generate."),
    output_dir: str = typer.Option("output", help="Output directory."),
    hcps: int | None = typer.Option(None, help="Number of HCPs to generate."),
    years: int | None = typer.Option(None, help="Number of years of data."),
    scenario: str | None = typer.Option(None, help="Scenario to simulate."),
    seed: int | None = typer.Option(None, help="Random seed for deterministic output."),
    output_format: str | None = typer.Option(
        None,
        "--output-format",
        help="Output format: csv, duckdb, or all.",
    ),
    config: str | None = typer.Option(
        None,
        "--config",
        help="Path to YAML configuration file.",
    ),
):
    """
    Generate synthetic healthcare commercial analytics data.
    """

    console.print("[bold green]HealthSynth generation started[/bold green]")
    start_time = time.perf_counter()

    datasets = run_generation(
        module=module,
        hcps=hcps,
        years=years,
        scenario=scenario,
        output_dir=output_dir,
        seed=seed,
        config_path=config,
        output_format=output_format,
    )

    elapsed_seconds = time.perf_counter() - start_time

    console.print("[bold green]Generation complete[/bold green]")
    if "market" in datasets:
        console.print(f"Created {len(datasets['market'])} market records")
    console.print(f"Created {len(datasets['hcp_master'])} HCP records")
    console.print(f"Created {len(datasets['product'])} product records")
    if "market_share" in datasets:
        console.print(f"Created {len(datasets['market_share'])} market share records")
    console.print(f"Created {len(datasets['call_activity'])} call activity records")
    console.print(f"Created {len(datasets['prescriptions'])} prescription records")
    if "market_demand" in datasets:
        console.print(f"Created {len(datasets['market_demand'])} market demand records")
    if output_format in ["duckdb", "all"]:
        console.print(f"Created DuckDB database: {output_dir}/healthsynth.duckdb")
    if output_format in ["csv", "all"]:
        console.print("Created CSV files")
    console.print(f"Created validation report: {output_dir}/validation_report.md")
    console.print(f"Output written to: {output_dir}")
    console.print(f"Generation time: {elapsed_seconds:.2f} seconds")
    timings = datasets.get("_timings", {})

    if timings:
        console.print("")
        console.print("[bold]Timing breakdown[/bold]")
        for step, seconds in timings.items():
            console.print(f"- {step}: {seconds:.2f}s")


if __name__ == "__main__":
    app()
