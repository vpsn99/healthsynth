import pandas as pd

from healthsynth.generator import generate


def test_generate_returns_expected_tables(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    expected_tables = {
        "hcp_master",
        "product",
        "call_activity",
        "prescriptions",
        "market",
        "market_share",
    }

    assert expected_tables.issubset(set(datasets.keys()))


def test_generate_returns_timing_metadata(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    assert "_timings" in datasets
    assert "simulation" in datasets["_timings"]
    assert "validation" in datasets["_timings"]
    assert "total" in datasets["_timings"]


def test_generation_settings_can_come_from_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
generation:
  hcps: 12
  years: 2
  seed: 123
  output_format: csv
""",
        encoding="utf-8",
    )

    datasets = generate(
        output_dir=str(tmp_path),
        config_path=str(config_file),
    )

    assert len(datasets["hcp_master"]) == 12
    assert len(datasets["prescriptions"]) == 12 * 24 * len(datasets["product"])


def test_cli_style_arguments_override_yaml_generation_settings(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
generation:
  hcps: 12
  years: 2
  seed: 123
  output_format: csv
""",
        encoding="utf-8",
    )

    datasets = generate(
        hcps=20,
        years=1,
        output_dir=str(tmp_path),
        config_path=str(config_file),
    )

    assert len(datasets["hcp_master"]) == 20
    assert len(datasets["prescriptions"]) == 20 * 12 * len(datasets["product"])


def test_hcp_count_is_correct(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    assert len(datasets["hcp_master"]) == 5


def test_prescription_count_matches_hcps_months_and_products(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    product_count = len(datasets["product"])

    assert len(datasets["prescriptions"]) == 5 * 12 * product_count


def test_multiple_channels_are_generated(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    channels = set(datasets["call_activity"]["channel"])

    assert len(channels) > 1


def test_csv_outputs_are_created_by_default(tmp_path):
    generate(
        hcps=10,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    assert (tmp_path / "hcp_master.csv").exists()
    assert (tmp_path / "product.csv").exists()
    assert (tmp_path / "call_activity.csv").exists()
    assert (tmp_path / "prescriptions.csv").exists()
    assert (tmp_path / "market.csv").exists()
    assert (tmp_path / "validation_report.md").exists()
    assert not (tmp_path / "healthsynth.duckdb").exists()


def test_all_output_format_creates_csv_and_duckdb(tmp_path):
    generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
        output_format="all",
    )

    assert (tmp_path / "hcp_master.csv").exists()
    assert (tmp_path / "product.csv").exists()
    assert (tmp_path / "call_activity.csv").exists()
    assert (tmp_path / "prescriptions.csv").exists()
    assert (tmp_path / "market.csv").exists()
    assert (tmp_path / "healthsynth.duckdb").exists()
    assert (tmp_path / "validation_report.md").exists()


def test_duckdb_output_format_creates_only_duckdb(tmp_path):
    generate(
        hcps=10,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
        output_format="duckdb",
    )

    assert (tmp_path / "healthsynth.duckdb").exists()
    assert (tmp_path / "validation_report.md").exists()
    assert not (tmp_path / "hcp_master.csv").exists()


def test_referential_integrity(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    market_ids = set(datasets["market"]["market_id"])
    hcp_ids = set(datasets["hcp_master"]["hcp_id"])
    product_ids = set(datasets["product"]["product_id"])

    assert set(datasets["hcp_master"]["market_id"]).issubset(market_ids)
    assert set(datasets["product"]["market_id"]).issubset(market_ids)
    assert set(datasets["call_activity"]["market_id"]).issubset(market_ids)
    assert set(datasets["prescriptions"]["market_id"]).issubset(market_ids)
    assert set(datasets["call_activity"]["hcp_id"]).issubset(hcp_ids)
    assert set(datasets["prescriptions"]["hcp_id"]).issubset(hcp_ids)
    assert set(datasets["call_activity"]["product_id"]).issubset(product_ids)
    assert set(datasets["prescriptions"]["product_id"]).issubset(product_ids)


def test_generation_is_deterministic(tmp_path):
    first = generate(
        hcps=20,
        years=1,
        output_dir=str(tmp_path / "run1"),
        seed=123,
    )

    second = generate(
        hcps=20,
        years=1,
        output_dir=str(tmp_path / "run2"),
        seed=123,
    )

    pd.testing.assert_frame_equal(first["hcp_master"], second["hcp_master"])
    pd.testing.assert_frame_equal(first["product"], second["product"])
    pd.testing.assert_frame_equal(first["call_activity"], second["call_activity"])
    pd.testing.assert_frame_equal(first["prescriptions"], second["prescriptions"])
    pd.testing.assert_frame_equal(first["market"], second["market"])


def test_generate_accepts_config_path(tmp_path):
    config_file = tmp_path / "custom.yaml"
    config_file.write_text(
        """
num_territories: 5
""",
        encoding="utf-8",
    )

    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    territory_count = datasets["hcp_master"]["territory_id"].nunique()

    assert territory_count <= 5


def test_market_table_is_generated(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    market = datasets["market"]

    assert len(market) == 1
    assert {"market_id", "market_name", "country", "locale", "profile_name"}.issubset(
        market.columns
    )


def test_market_share_table_is_generated(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    market_share = datasets["market_share"]

    assert len(market_share) == 2 * 12
    assert {
        "market_id",
        "month",
        "therapeutic_area",
        "product_id",
        "baseline_market_share",
        "adjusted_market_share",
    }.issubset(market_share.columns)


def test_market_share_sums_to_one_by_month_and_therapeutic_area(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    market_share = datasets["market_share"]

    totals = market_share.groupby(["therapeutic_area", "month"])["adjusted_market_share"].sum()

    assert all(abs(total - 1.0) <= 0.001 for total in totals)


def test_promotion_effect_table_is_generated(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    promotion_effect = datasets["promotion_effect"]

    assert len(promotion_effect) > 0
    assert {
        "market_id",
        "month",
        "product_id",
        "promotion_score",
        "promotion_index",
    }.issubset(promotion_effect.columns)


def test_promotion_index_is_between_zero_and_one(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    promotion_effect = datasets["promotion_effect"]

    assert promotion_effect["promotion_index"].between(0, 1).all()


def test_market_demand_table_is_generated(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    market_demand = datasets["market_demand"]

    assert len(market_demand) == 12
    assert {
        "market_id",
        "month",
        "therapeutic_area",
        "base_market_nrx",
        "growth_factor",
        "seasonality_factor",
        "market_nrx",
    }.issubset(market_demand.columns)


def test_market_demand_is_positive(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    assert (datasets["market_demand"]["market_nrx"] >= 0).all()


def test_prescriptions_match_monthly_market_demand(tmp_path):
    datasets = generate(
        config_path="configs/profiles/test_minimal.yaml",
        output_dir=str(tmp_path),
    )

    rx = datasets["prescriptions"].copy()
    demand = datasets["market_demand"].copy()
    products = datasets["product"][["product_id", "therapeutic_area"]]

    rx["month"] = pd.to_datetime(rx["rx_date"]).dt.strftime("%Y-%m")
    demand["month"] = pd.to_datetime(demand["month"]).dt.strftime("%Y-%m")

    actual = (
        rx.merge(products, on="product_id")
        .groupby(["market_id", "month", "therapeutic_area"])["nrx"]
        .sum()
        .reset_index(name="actual_nrx")
    )

    expected = demand[["market_id", "month", "therapeutic_area", "market_nrx"]]

    comparison = actual.merge(
        expected,
        on=["market_id", "month", "therapeutic_area"],
    )

    assert (comparison["actual_nrx"] == comparison["market_nrx"]).all()
