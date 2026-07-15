from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class SimulationSettings:
    scenario_name: str
    scenario_path: Path | None
    hcps: int
    years: int
    seed: int
    output_format: str


@dataclass
class SimulationSession:
    scenario_name: str
    output_dir: Path
    parameters: SimulationSettings
    results: dict
    dataframes: dict[str, pd.DataFrame]
