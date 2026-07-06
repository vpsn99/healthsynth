import typer
from rich.console import Console
from healthsynth.generator import generate as run_generation

app = typer.Typer(
    name="healthsynth",
    help="Synthetic pharma commercial analytics data generator.",
)

console = Console()


@app.callback()
def main():
    """
    HealthSynth CLI.
    """
    pass


@app.command()
def generate(
    module: str = typer.Option("commercial_analytics", help="Module to generate."),
    hcps: int = typer.Option(1000, help="Number of HCPs to generate."),
    years: int = typer.Option(3, help="Number of years of data."),
    scenario: str = typer.Option("new_product_launch", help="Scenario to simulate."),
    output_dir: str = typer.Option("output", help="Output directory."),
    seed: int = typer.Option(42, help="Random seed for deterministic output."),
):
    """
    Generate synthetic healthcare commercial analytics data.
    """

    console.print("[bold green]HealthSynth generation started[/bold green]")

    datasets = run_generation(
        module=module,
        hcps=hcps,
        years=years,
        scenario=scenario,
        output_dir=output_dir,
        seed=seed,
    )

    console.print("[bold green]Generation complete[/bold green]")
    console.print(f"Created {len(datasets['hcp_master'])} HCP records")
    console.print(f"Created {len(datasets['product'])} product records")
    console.print(f"Created {len(datasets['call_activity'])} call activity records")
    console.print(f"Created {len(datasets['prescriptions'])} prescription records")
    console.print(f"Output written to: {output_dir}")

if __name__ == "__main__":
    app()