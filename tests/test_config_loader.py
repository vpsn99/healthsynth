from pathlib import Path

import pytest

from healthsynth.config.loader import ConfigLoader
from healthsynth.exceptions import HealthSynthConfigurationError


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


def test_demo_config_contains_business_knowledge():
    config = ConfigLoader.load("configs/demo.yaml")

    assert len(config["products"]) == 3
    assert config["products"][0]["product_name"] == "CardioOne"
    assert "specialty_product_affinity" in config
    assert "channel_response_multiplier" in config


def test_demo_config_loads_successfully():
    config_path = Path("configs/demo.yaml")

    config = ConfigLoader.load(str(config_path))

    assert config["locale"] == "en_CA"
    assert config["num_territories"] == 20


def test_config_validation_rejects_invalid_channel_distribution(tmp_path):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
channel_distribution:
  Rep Call: 0.90
  Email: 0.90
""",
        encoding="utf-8",
    )

    with pytest.raises(HealthSynthConfigurationError):
        ConfigLoader.load(str(config_file))


def test_config_validation_rejects_duplicate_product_ids(tmp_path):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
  - product_id: P001
    product_name: Product Two
""",
        encoding="utf-8",
    )

    with pytest.raises(HealthSynthConfigurationError):
        ConfigLoader.load(str(config_file))


def test_config_validation_rejects_unknown_affinity_product(tmp_path):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
specialty_product_affinity:
  Cardiology:
    UNKNOWN_PRODUCT: 1.0
""",
        encoding="utf-8",
    )

    with pytest.raises(HealthSynthConfigurationError):
        ConfigLoader.load(str(config_file))


def test_config_validation_rejects_negative_generation_values(tmp_path):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
generation:
  hcps: -10
""",
        encoding="utf-8",
    )

    with pytest.raises(HealthSynthConfigurationError):
        ConfigLoader.load(str(config_file))


def test_product_configuration_contains_competitor_ready_fields():
    config = ConfigLoader.load("configs/profiles/oncology_training.yaml")

    products = config["products"]

    required_fields = {
        "manufacturer",
        "brand_type",
        "baseline_market_share",
    }

    for product in products:
        assert required_fields.issubset(product.keys())


def test_baseline_market_share_sums_to_one_by_therapeutic_area():
    config = ConfigLoader.load("configs/profiles/oncology_training.yaml")

    products = config["products"]
    shares_by_area = {}

    for product in products:
        area = product["therapeutic_area"]
        shares_by_area[area] = shares_by_area.get(area, 0.0) + float(
            product["baseline_market_share"]
        )

    for total_share in shares_by_area.values():
        assert abs(total_share - 1.0) <= 0.01


def test_config_validation_rejects_invalid_market_share_sum(tmp_path):
    config_file = tmp_path / "bad_market_share.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    therapeutic_area: Oncology
    manufacturer: NVA Pharma
    brand_type: Innovator
    baseline_market_share: 0.80

  - product_id: P002
    product_name: Product Two
    therapeutic_area: Oncology
    manufacturer: Competitor A
    brand_type: Competitor
    baseline_market_share: 0.80
""",
        encoding="utf-8",
    )

    with pytest.raises(HealthSynthConfigurationError):
        ConfigLoader.load(str(config_file))
