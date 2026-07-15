from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path
from uuid import uuid4

import pandas as pd
from models import SimulationSession, SimulationSettings

from healthsynth import generate


def dataframe_results(
    results: dict,
) -> dict[str, pd.DataFrame]:
    """Return only DataFrame objects from simulation results."""

    return {name: value for name, value in results.items() if isinstance(value, pd.DataFrame)}


def validate_simulation_inputs(
    settings: SimulationSettings,
) -> list[str]:
    """Return user-facing validation errors."""

    errors = []

    if settings.scenario_path is not None and not settings.scenario_path.exists():
        errors.append(f"Scenario profile does not exist: {settings.scenario_path}")

    if settings.hcps < 10:
        errors.append("At least 10 healthcare providers are required.")

    if settings.years < 1:
        errors.append("Simulation duration must be at least one year.")

    if settings.output_format not in {
        "csv",
        "duckdb",
        "all",
    }:
        errors.append(f"Unsupported output format: {settings.output_format}")

    return errors


def create_run_id() -> str:
    """Create a collision-resistant simulation run ID."""

    return f"{time.strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"


def run_simulation(
    settings: SimulationSettings,
    output_root: Path,
) -> SimulationSession:
    """Run HealthSynth and return a structured UI session."""

    output_dir = output_root / create_run_id()

    generation_arguments = {
        "hcps": settings.hcps,
        "years": settings.years,
        "seed": settings.seed,
        "output_dir": str(output_dir),
        "output_format": settings.output_format,
    }

    if settings.scenario_path is not None:
        generation_arguments["config_path"] = str(settings.scenario_path)

    results = generate(**generation_arguments)
    dataframes = dataframe_results(results)

    return SimulationSession(
        scenario_name=settings.scenario_name,
        output_dir=output_dir,
        parameters=settings,
        results=results,
        dataframes=dataframes,
    )


def build_output_zip(output_dir: Path) -> bytes:
    """Create an in-memory ZIP containing one simulation run."""

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                archive.write(
                    file_path,
                    arcname=file_path.relative_to(output_dir),
                )

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
