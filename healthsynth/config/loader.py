from pathlib import Path

import yaml

from healthsynth.config.defaults import DEFAULT_CONFIG
from healthsynth.config.merge import deep_merge


class ConfigLoader:
    @staticmethod
    def load(config_path: str | None = None) -> dict:
        """
        Load HealthSynth configuration.

        If config_path is provided, YAML values override defaults.
        If no config_path is provided, defaults are returned.
        """
        if config_path is None:
            return deep_merge(DEFAULT_CONFIG, None)

        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with path.open("r", encoding="utf-8") as file:
            yaml_config = yaml.safe_load(file) or {}

        return deep_merge(DEFAULT_CONFIG, yaml_config)
