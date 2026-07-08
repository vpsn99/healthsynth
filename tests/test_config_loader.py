from pathlib import Path

import pytest

from healthsynth.config.loader import ConfigLoader


def test_config_loader_returns_defaults_without_path():
    config = ConfigLoader.load()

    assert "products" in config
    assert "specialty_distribution" in config
    assert "channel_distribution" in config


def test_config_loader_merges_yaml_overrides(tmp_path):
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(
        """
num_territories: 99

channel_distribution:
  Rep Call: 0.80
  Email: 0.20
""",
        encoding="utf-8",
    )

    config = ConfigLoader.load(str(config_file))

    assert config["num_territories"] == 99
    assert config["channel_distribution"]["Rep Call"] == 0.80
    assert config["channel_distribution"]["Email"] == 0.20

    # Values not specified in YAML should still come from defaults.
    assert "products" in config
    assert "specialty_distribution" in config


def test_config_loader_raises_for_missing_file():
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load("missing_config.yaml")


def test_demo_config_loads_successfully():
    config_path = Path("configs/demo.yaml")

    config = ConfigLoader.load(str(config_path))

    assert config["locale"] == "en_CA"
    assert config["num_territories"] == 20
