from pathlib import Path

import yaml

from healthsynth.config.defaults import DEFAULT_CONFIG
from healthsynth.config.merge import deep_merge
from healthsynth.config.validator import validate_config


class ConfigLoader:
    @staticmethod
    def load(config_path: str | None = None) -> dict:
        """
        Load HealthSynth configuration.

        If config_path is provided, YAML values override defaults.
        If no config_path is provided, defaults are returned.
        """
        if config_path is None:
            config = deep_merge(DEFAULT_CONFIG, None)
            validate_config(config)
            return config

        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with path.open("r", encoding="utf-8") as file:
            yaml_config = yaml.safe_load(file) or {}

        config = deep_merge(DEFAULT_CONFIG, yaml_config)
        validate_config(config)
        return config
