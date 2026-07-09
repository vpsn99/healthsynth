from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def write_manifest(
    *,
    output_dir: str,
    datasets: dict,
    config: dict,
    output_format: str,
    version: str = "0.1.0",
) -> None:
    """
    Write a HealthSynth dataset manifest describing the generated output.
    """

    manifest = {
        "healthsynth_version": version,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "profile": config.get("profile_name", "custom"),
        "scenario": config.get("scenario_name", "default"),
        "locale": config.get("locale"),
        "seed": config.get("generation", {}).get("seed"),
        "output_format": output_format,
        "timings": datasets.get("_timings", {}),
        "datasets": {name: len(df) for name, df in datasets.items() if not name.startswith("_")},
    }

    output_path = Path(output_dir)

    with open(
        output_path / "healthsynth_manifest.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(manifest, f, indent=2)
