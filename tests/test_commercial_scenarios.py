import pandas as pd
import pytest

from healthsynth.commercial.dynamics import (
    MarketShareGenerator,
    generate_market_share,
)
from healthsynth.commercial.facts import generate_call_activity


@pytest.fixture
def call_activity_inputs():
    config = {
        "market": {
            "market_id": "MKT_TEST",
            "market_name": "Test Market",
            "country": "Canada",
        },
        "channel_distribution": {
            "Rep Call": 1.0,
        },
    }

    hcps = pd.DataFrame(
        [
            {
                "hcp_id": "HCP001",
                "rep_id": "REP001",
                "segment": "High",
                "decile": 10,
            },
            {
                "hcp_id": "HCP002",
                "rep_id": "REP001",
                "segment": "Medium",
                "decile": 5,
            },
        ]
    )

    products = pd.DataFrame(
        [
            {
                "product_id": "P001",
                "product_name": "EstablishedBrand",
                "launch_date": "2022-01-01",
            },
            {
                "product_id": "P003",
                "product_name": "LaunchBrand",
                "launch_date": "2023-05-01",
            },
        ]
    )

    return {
        "config": config,
        "hcps": hcps,
        "products": products,
    }


@pytest.fixture
def launch_market_share():
    config = {
        "market": {
            "market_id": "MKT_TEST",
            "market_name": "Test Market",
            "country": "Canada",
        }
    }

    products = pd.DataFrame(
        [
            {
                "market_id": "MKT_TEST",
                "product_id": "P001",
                "product_name": "EstablishedBrand",
                "therapeutic_area": "Oncology",
                "launch_date": "2022-01-01",
                "baseline_market_share": 0.80,
            },
            {
                "market_id": "MKT_TEST",
                "product_id": "P002",
                "product_name": "LaunchBrand",
                "therapeutic_area": "Oncology",
                "launch_date": "2023-05-01",
                "baseline_market_share": 0.20,
                "adoption_curve": "linear",
                "adoption_months": 8,
                "launch_share_factor": 0.10,
                "promotion_adoption_weight": 0.25,
            },
        ]
    )

    promotion_effect = pd.DataFrame(
        [
            {
                "market_id": "MKT_TEST",
                "month": "2023-05",
                "product_id": "P002",
                "promotion_score": 10.0,
                "promotion_index": 0.80,
            },
            {
                "market_id": "MKT_TEST",
                "month": "2023-06",
                "product_id": "P002",
                "promotion_score": 10.0,
                "promotion_index": 0.80,
            },
        ]
    )

    return generate_market_share(
        product=products,
        promotion_effect=promotion_effect,
        years=2,
        seed=42,
        config=config,
    )


@pytest.fixture
def share_redistribution_setup():
    generator = MarketShareGenerator(
        seed=42,
        config={
            "market": {
                "market_id": "MKT_TEST",
            }
        },
    )

    area_products = pd.DataFrame(
        [
            {
                "product_id": "P001",
                "therapeutic_area": "Oncology",
            },
            {
                "product_id": "P002",
                "therapeutic_area": "Oncology",
            },
            {
                "product_id": "P003",
                "therapeutic_area": "Oncology",
                "share_source_weights": {
                    "P001": 0.35,
                    "P002": 0.65,
                },
            },
        ]
    )

    return generator, area_products


def test_market_share_is_zero_before_product_launch(launch_market_share):
    pre_launch = launch_market_share[
        (launch_market_share["product_id"] == "P002")
        & (pd.to_datetime(launch_market_share["month"]) < pd.Timestamp("2023-05-01"))
    ]

    assert not pre_launch.empty
    assert (pre_launch["adjusted_market_share"] == 0.0).all()


def test_market_share_is_positive_from_launch_month(launch_market_share):
    launch_and_after = launch_market_share[
        (launch_market_share["product_id"] == "P002")
        & (pd.to_datetime(launch_market_share["month"]) >= pd.Timestamp("2023-05-01"))
    ]

    assert not launch_and_after.empty
    assert (launch_and_after["adjusted_market_share"] > 0.0).all()


def test_monthly_market_share_sums_to_one(launch_market_share):
    totals = (
        launch_market_share.groupby(["therapeutic_area", "month"])["adjusted_market_share"]
        .sum()
        .round(10)
    )

    assert (totals == 1.0).all()


def test_launch_product_adoption_starts_below_full_potential(
    launch_market_share,
):
    launch_row = launch_market_share[
        (launch_market_share["product_id"] == "P002")
        & (pd.to_datetime(launch_market_share["month"]) == pd.Timestamp("2023-05-01"))
    ].iloc[0]

    assert launch_row["base_adoption_factor"] == pytest.approx(0.10)


def test_launch_product_adoption_increases_over_time(
    launch_market_share,
):
    launch_product = launch_market_share[launch_market_share["product_id"] == "P002"].copy()

    launch_product["month"] = pd.to_datetime(launch_product["month"])

    post_launch = launch_product[launch_product["month"] >= pd.Timestamp("2023-05-01")].sort_values(
        "month"
    )

    factors = post_launch["base_adoption_factor"].tolist()

    assert factors == sorted(factors)
    assert factors[0] == pytest.approx(0.10)


def test_launch_product_reaches_full_adoption(
    launch_market_share,
):
    mature_row = launch_market_share[
        (launch_market_share["product_id"] == "P002")
        & (pd.to_datetime(launch_market_share["month"]) == pd.Timestamp("2024-01-01"))
    ].iloc[0]

    assert mature_row["base_adoption_factor"] == pytest.approx(1.0)


def test_existing_product_is_fully_adopted(
    launch_market_share,
):
    incumbent = launch_market_share[launch_market_share["product_id"] == "P001"]

    assert (incumbent["base_adoption_factor"] == 1.0).all()


def test_effective_adoption_is_not_below_base_adoption(
    launch_market_share,
):
    launch_product = launch_market_share[launch_market_share["product_id"] == "P002"]

    assert (
        launch_product["effective_adoption_factor"] >= launch_product["base_adoption_factor"]
    ).all()


def test_effective_adoption_does_not_exceed_one(
    launch_market_share,
):
    assert (launch_market_share["effective_adoption_factor"] <= 1.0).all()


def test_product_without_promotion_weight_has_no_acceleration(
    launch_market_share,
):
    incumbent = launch_market_share[launch_market_share["product_id"] == "P001"]

    assert (incumbent["promotion_acceleration"] == 0.0).all()


def test_promotion_accelerates_launch_adoption(
    launch_market_share,
):
    launch_row = launch_market_share[
        (launch_market_share["product_id"] == "P002")
        & (pd.to_datetime(launch_market_share["month"]) == pd.Timestamp("2023-05-01"))
    ].iloc[0]

    assert launch_row["promotion_acceleration"] > 0.0

    assert launch_row["effective_adoption_factor"] > launch_row["base_adoption_factor"]


def test_promotion_acceleration_is_zero_before_launch(
    launch_market_share,
):
    pre_launch = launch_market_share[
        (launch_market_share["product_id"] == "P002")
        & (pd.to_datetime(launch_market_share["month"]) < pd.Timestamp("2023-05-01"))
    ]

    assert (pre_launch["promotion_acceleration"] == 0.0).all()


def test_call_activity_excludes_products_before_launch(
    call_activity_inputs,
):
    calls = generate_call_activity(
        hcp_master=call_activity_inputs["hcps"],
        product=call_activity_inputs["products"],
        years=1,
        seed=42,
        config=call_activity_inputs["config"],
    )

    launch_calls = calls[calls["product_id"] == "P003"].copy()

    launch_calls["call_date"] = pd.to_datetime(launch_calls["call_date"])

    assert (launch_calls["call_date"] >= pd.Timestamp("2023-05-01")).all()


def test_launch_product_receives_calls_after_launch(
    call_activity_inputs,
):
    calls = generate_call_activity(
        hcp_master=call_activity_inputs["hcps"],
        product=call_activity_inputs["products"],
        years=1,
        seed=42,
        config=call_activity_inputs["config"],
    )

    launch_calls = calls[calls["product_id"] == "P003"]

    assert not launch_calls.empty


def test_share_redistribution_takes_more_from_higher_weighted_incumbent(
    share_redistribution_setup,
):
    generator, area_products = share_redistribution_setup

    normalized_shares = {
        "P001": 0.50,
        "P002": 0.40,
        "P003": 0.10,
    }

    redistributed = generator._apply_share_redistribution(
        normalized_shares=normalized_shares,
        area_products=area_products,
        month_start=pd.Timestamp("2023-05-01"),
    )

    incumbent_market = 1.0 - normalized_shares["P003"]

    p001_before_redistribution = normalized_shares["P001"] / incumbent_market
    p002_before_redistribution = normalized_shares["P002"] / incumbent_market

    p001_loss = p001_before_redistribution - redistributed["P001"]
    p002_loss = p002_before_redistribution - redistributed["P002"]

    assert p001_loss == pytest.approx(0.035)
    assert p002_loss == pytest.approx(0.065)
    assert p002_loss > p001_loss


def test_share_redistribution_preserves_total_market_share(
    share_redistribution_setup,
):
    generator, area_products = share_redistribution_setup

    redistributed = generator._apply_share_redistribution(
        normalized_shares={
            "P001": 0.50,
            "P002": 0.40,
            "P003": 0.10,
        },
        area_products=area_products,
        month_start=pd.Timestamp("2023-05-01"),
    )

    assert sum(redistributed.values()) == pytest.approx(1.0)
    assert all(share >= 0.0 for share in redistributed.values())


def test_share_source_weights_have_no_effect_before_launch(
    share_redistribution_setup,
):
    generator, area_products = share_redistribution_setup

    normalized_shares = {
        "P001": 0.55,
        "P002": 0.45,
        "P003": 0.00,
    }

    redistributed = generator._apply_share_redistribution(
        normalized_shares=normalized_shares,
        area_products=area_products,
        month_start=pd.Timestamp("2023-04-01"),
    )

    assert redistributed == normalized_shares
