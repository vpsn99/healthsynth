import pandas as pd
import pytest

from healthsynth.generator import generate


@pytest.mark.slow
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


@pytest.mark.slow
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


@pytest.mark.slow
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


@pytest.mark.slow
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


@pytest.mark.slow
def test_market_share_influences_prescription_distribution(tmp_path):
    datasets = generate(
        config_path="configs/profiles/oncology_training.yaml",
        output_dir=str(tmp_path),
    )

    rx = datasets["prescriptions"]
    product = datasets["product"]

    rx_by_product = (
        rx.groupby("product_id")["nrx"]
        .sum()
        .reset_index()
        .merge(
            product[["product_id", "baseline_market_share"]],
            on="product_id",
        )
        .sort_values("baseline_market_share", ascending=False)
    )

    top_share_product = rx_by_product.iloc[0]["product_id"]
    top_rx_product = rx_by_product.sort_values(
        "nrx",
        ascending=False,
    ).iloc[0]["product_id"]

    assert top_share_product == top_rx_product


@pytest.mark.slow
def test_oncology_profile_end_to_end(tmp_path):
    datasets = generate(
        config_path="configs/profiles/oncology_training.yaml",
        output_dir=str(tmp_path),
    )

    assert len(datasets["hcp_master"]) == 1000
    assert len(datasets["product"]) == 3
    assert len(datasets["market_share"]) == 108
