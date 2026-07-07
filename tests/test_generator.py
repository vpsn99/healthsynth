import pandas as pd

from healthsynth.generator import generate


def test_generate_returns_expected_tables(tmp_path):
    datasets = generate(
        hcps=10,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    assert set(datasets.keys()) == {
        "hcp_master",
        "product",
        "call_activity",
        "prescriptions",
    }


def test_hcp_count_is_correct(tmp_path):
    datasets = generate(
        hcps=25,
        years=1,
        output_dir=str(tmp_path),
        seed=42,
    )

    assert len(datasets["hcp_master"]) == 25


def test_prescription_count_matches_hcps_and_months(tmp_path):
    datasets = generate(
        hcps=25,
        years=2,
        output_dir=str(tmp_path),
        seed=42,
    )

    assert len(datasets["prescriptions"]) == 25 * 24


def test_outputs_are_created(tmp_path):
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
    assert (tmp_path / "healthsynth.duckdb").exists()
    assert (tmp_path / "validation_report.md").exists()


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
