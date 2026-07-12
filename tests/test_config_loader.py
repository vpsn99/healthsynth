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


def test_config_validation_accepts_valid_share_source_weights(
    tmp_path,
):
    config_file = tmp_path / "valid_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.45
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Oncology
    baseline_market_share: 0.35
    launch_date: "2022-01-01"

  - product_id: P003
    product_name: Launch Product
    manufacturer: Pharma C
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.20
    launch_date: "2023-05-01"
    share_source_weights:
      P001: 0.35
      P002: 0.65
""",
        encoding="utf-8",
    )

    config = ConfigLoader.load(str(config_file))

    assert config["products"][2]["share_source_weights"] == {
        "P001": 0.35,
        "P002": 0.65,
    }


def test_config_validation_rejects_share_source_weights_not_summing_to_one(
    tmp_path,
):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.45
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Oncology
    baseline_market_share: 0.35
    launch_date: "2022-01-01"

  - product_id: P003
    product_name: Launch Product
    manufacturer: Pharma C
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.20
    launch_date: "2023-05-01"
    share_source_weights:
      P001: 0.20
      P002: 0.30
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="share_source_weights must sum",
    ):
        ConfigLoader.load(str(config_file))


def test_config_validation_rejects_share_source_self_reference(
    tmp_path,
):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.45
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Oncology
    baseline_market_share: 0.35
    launch_date: "2022-01-01"

  - product_id: P003
    product_name: Launch Product
    manufacturer: Pharma C
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.20
    launch_date: "2023-05-01"
    share_source_weights:
      P001: 0.50
      P003: 0.50
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="cannot reference the same product",
    ):
        ConfigLoader.load(str(config_file))


def test_config_validation_rejects_unknown_share_source_product(
    tmp_path,
):
    config_file = tmp_path / "bad_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.45
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Oncology
    baseline_market_share: 0.35
    launch_date: "2022-01-01"

  - product_id: P003
    product_name: Launch Product
    manufacturer: Pharma C
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.20
    launch_date: "2023-05-01"
    share_source_weights:
      P001: 0.50
      P999: 0.50
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="references unknown product",
    ):
        ConfigLoader.load(str(config_file))


def test_config_validation_accepts_valid_loe_configuration(
    tmp_path,
):
    config_file = tmp_path / "valid_loe_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Cardiology
    baseline_market_share: 0.50
    launch_date: "2022-01-01"
    loe_date: "2024-01-01"
    loe_erosion_months: 8
    post_loe_share_factor: 0.30

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.30
    launch_date: "2022-01-01"

  - product_id: P003
    product_name: Product Three
    manufacturer: Pharma C
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.20
    launch_date: "2022-01-01"
""",
        encoding="utf-8",
    )

    config = ConfigLoader.load(str(config_file))

    assert config["products"][0]["loe_date"] == "2024-01-01"
    assert config["products"][0]["loe_erosion_months"] == 8
    assert config["products"][0]["post_loe_share_factor"] == 0.30


def test_config_validation_rejects_non_positive_loe_erosion_months(
    tmp_path,
):
    config_file = tmp_path / "bad_loe_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.60
    launch_date: "2022-01-01"
    loe_date: "2024-01-01"
    loe_erosion_months: 0
    post_loe_share_factor: 0.30

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Oncology
    baseline_market_share: 0.40
    launch_date: "2022-01-01"
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="loe_erosion_months must be greater than 0",
    ):
        ConfigLoader.load(str(config_file))


def test_config_validation_rejects_post_loe_share_factor_above_one(
    tmp_path,
):
    config_file = tmp_path / "bad_loe_config.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Oncology
    baseline_market_share: 0.60
    launch_date: "2022-01-01"
    loe_date: "2024-01-01"
    loe_erosion_months: 8
    post_loe_share_factor: 1.20

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Oncology
    baseline_market_share: 0.40
    launch_date: "2022-01-01"
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="post_loe_share_factor must be between 0 and 1",
    ):
        ConfigLoader.load(str(config_file))


def test_config_validation_accepts_valid_market_access_configuration(
    tmp_path,
):
    config_file = tmp_path / "valid_market_access.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Cardiology
    baseline_market_share: 0.50
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.30
    launch_date: "2022-01-01"
    market_access_date: "2024-01-01"
    market_access_factor: 1.25

  - product_id: P003
    product_name: Product Three
    manufacturer: Pharma C
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.20
    launch_date: "2022-01-01"
""",
        encoding="utf-8",
    )

    config = ConfigLoader.load(str(config_file))

    assert config["products"][1]["market_access_date"] == "2024-01-01"
    assert config["products"][1]["market_access_factor"] == 1.25


def test_config_validation_rejects_non_positive_market_access_factor(
    tmp_path,
):
    config_file = tmp_path / "bad_market_access.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Cardiology
    baseline_market_share: 0.50
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.30
    launch_date: "2022-01-01"
    market_access_date: "2024-01-01"
    market_access_factor: 0

  - product_id: P003
    product_name: Product Three
    manufacturer: Pharma C
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.20
    launch_date: "2022-01-01"
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="market_access_factor must be greater than 0",
    ):
        ConfigLoader.load(str(config_file))


def test_config_validation_requires_market_access_factor_with_date(
    tmp_path,
):
    config_file = tmp_path / "bad_market_access.yaml"
    config_file.write_text(
        """
products:
  - product_id: P001
    product_name: Product One
    manufacturer: Pharma A
    brand_type: Innovator
    therapeutic_area: Cardiology
    baseline_market_share: 0.50
    launch_date: "2022-01-01"

  - product_id: P002
    product_name: Product Two
    manufacturer: Pharma B
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.30
    launch_date: "2022-01-01"
    market_access_date: "2024-01-01"

  - product_id: P003
    product_name: Product Three
    manufacturer: Pharma C
    brand_type: Competitor
    therapeutic_area: Cardiology
    baseline_market_share: 0.20
    launch_date: "2022-01-01"
""",
        encoding="utf-8",
    )

    with pytest.raises(
        HealthSynthConfigurationError,
        match="market_access_factor is required",
    ):
        ConfigLoader.load(str(config_file))
