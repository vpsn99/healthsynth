import pandas as pd

from healthsynth.generator import generate


def test_generate_returns_expected_tables(tmp_path):
    datasets = generate(
        hcps=10,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    expected_tables = {
        "hcp_master",
        "product",
        "call_activity",
        "prescriptions",
    }

    assert expected_tables.issubset(set(datasets.keys()))


def test_generate_returns_timing_metadata(tmp_path):
    datasets = generate(
        hcps=10,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    assert "_timings" in datasets
    assert "simulation" in datasets["_timings"]
    assert "validation" in datasets["_timings"]
    assert "total" in datasets["_timings"]


def test_hcp_count_is_correct(tmp_path):
    datasets = generate(
        hcps=25,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    assert len(datasets["hcp_master"]) == 25


def test_specialty_product_affinity_affects_prescriptions(tmp_path):
    datasets = generate(
        hcps=500,
        years=2,
        output_dir=str(tmp_path),
        seed=42,
    )

    hcp_master = datasets["hcp_master"]
    prescriptions = datasets["prescriptions"]

    rx = prescriptions.merge(
        hcp_master[["hcp_id", "specialty"]],
        on="hcp_id",
        how="left",
    )

    specialty_product_nrx = rx.groupby(["specialty", "product_id"])["nrx"].sum().reset_index()

    cardiology = specialty_product_nrx[specialty_product_nrx["specialty"] == "Cardiology"]

    top_cardiology_product = cardiology.sort_values(
        "nrx",
        ascending=False,
    ).iloc[0]["product_id"]

    assert top_cardiology_product == "P001"


def test_prescription_count_matches_hcps_months_and_products(tmp_path):
    datasets = generate(
        hcps=25,
        years=2,
        output_dir=str(tmp_path),
        seed=42,
    )

    product_count = len(datasets["product"])

    assert len(datasets["prescriptions"]) == 25 * 24 * product_count


def test_multiple_channels_are_generated(tmp_path):
    datasets = generate(
        hcps=100,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
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
    assert (tmp_path / "validation_report.md").exists()
    assert not (tmp_path / "healthsynth.duckdb").exists()


def test_all_output_format_creates_csv_and_duckdb(tmp_path):
    generate(
        hcps=10,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
        output_format="all",
    )

    assert (tmp_path / "hcp_master.csv").exists()
    assert (tmp_path / "product.csv").exists()
    assert (tmp_path / "call_activity.csv").exists()
    assert (tmp_path / "prescriptions.csv").exists()
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
        hcps=50,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    hcp_ids = set(datasets["hcp_master"]["hcp_id"])
    product_ids = set(datasets["product"]["product_id"])

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


def test_high_segment_hcps_receive_more_calls(tmp_path):
    datasets = generate(
        hcps=500,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    hcp_master = datasets["hcp_master"]
    call_activity = datasets["call_activity"]

    calls_with_segment = call_activity.merge(
        hcp_master[["hcp_id", "segment"]],
        on="hcp_id",
        how="left",
    )

    calls_per_hcp = (
        calls_with_segment.groupby("segment").size() / hcp_master.groupby("segment").size()
    )

    assert calls_per_hcp["High"] > calls_per_hcp["Medium"]
    assert calls_per_hcp["Medium"] > calls_per_hcp["Low"]


def test_high_deciles_generate_more_prescriptions(tmp_path):
    datasets = generate(
        hcps=500,
        years=3,
        output_dir=str(tmp_path),
        seed=42,
    )

    hcp_master = datasets["hcp_master"]
    prescriptions = datasets["prescriptions"]

    rx_with_decile = prescriptions.merge(
        hcp_master[["hcp_id", "decile"]],
        on="hcp_id",
        how="left",
    )

    rx_per_hcp_by_decile = (
        rx_with_decile.groupby("decile")["nrx"].sum() / hcp_master.groupby("decile").size()
    )

    assert rx_per_hcp_by_decile.loc[10] > rx_per_hcp_by_decile.loc[1]


def test_new_product_launch_drives_adoption(tmp_path):
    datasets = generate(
        hcps=100,
        years=3,
        output_dir=str(tmp_path),
        seed=42,
    )

    rx = datasets["prescriptions"].copy()
    rx["rx_date"] = pd.to_datetime(rx["rx_date"])

    monthly = rx.groupby(rx["rx_date"].dt.to_period("M"))["nrx"].sum().sort_index()

    early_avg = monthly.iloc[:6].mean()
    late_avg = monthly.iloc[-6:].mean()

    assert late_avg > early_avg


def test_generate_accepts_config_path(tmp_path):
    config_file = tmp_path / "custom.yaml"
    config_file.write_text(
        """
num_territories: 5
""",
        encoding="utf-8",
    )

    datasets = generate(
        hcps=50,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
        config_path=str(config_file),
    )

    territory_count = datasets["hcp_master"]["territory_id"].nunique()

    assert territory_count <= 5
