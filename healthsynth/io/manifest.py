from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from healthsynth.metadata import (
    PACKAGE_VERSION,
    SCHEMA_VERSION,
)


def write_manifest(
    *,
    output_dir: str,
    datasets: dict,
    config: dict,
    output_format: str,
) -> None:
    """
    Write a HealthSynth dataset manifest describing the generated output.
    """
    timings = {key: round(value, 2) for key, value in datasets.get("_timings", {}).items()}

    manifest = {
        "healthsynth_version": PACKAGE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "market": {
            "market_id": config["market"]["market_id"],
            "market_name": config["market"]["market_name"],
            "country": config["market"]["country"],
            "locale": config.get("locale"),
        },
        "profile": config.get("profile_name", "custom"),
        "scenario": config.get("scenario_name", "default"),
        "seed": config.get("generation", {}).get("seed"),
        "generation": config.get("generation", {}),
        "output_format": output_format,
        "timings": timings,
        "datasets": {name: len(df) for name, df in datasets.items() if not name.startswith("_")},
    }

    output_path = Path(output_dir)

    with open(
        output_path / "healthsynth_manifest.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(manifest, f, indent=2)
