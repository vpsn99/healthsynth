import pandas as pd
import pytest

from healthsynth.commercial.events.market_access import (
    calculate_market_access_factor,
)


@pytest.fixture
def improved_access_product():
    return pd.Series(
        {
            "product_id": "P002",
            "market_access_date": "2024-01-01",
            "market_access_factor": 1.25,
        }
    )


def test_market_access_factor_is_one_before_access_change(
    improved_access_product,
):
    factor = calculate_market_access_factor(
        product_row=improved_access_product,
        month_start=pd.Timestamp("2023-12-01"),
    )

    assert factor == pytest.approx(1.0)


def test_market_access_factor_applies_from_access_month(
    improved_access_product,
):
    factor = calculate_market_access_factor(
        product_row=improved_access_product,
        month_start=pd.Timestamp("2024-01-01"),
    )

    assert factor == pytest.approx(1.25)


def test_restricted_access_reduces_competitive_factor():
    product = pd.Series(
        {
            "product_id": "P003",
            "market_access_date": "2024-01-01",
            "market_access_factor": 0.70,
        }
    )

    factor = calculate_market_access_factor(
        product_row=product,
        month_start=pd.Timestamp("2024-06-01"),
    )

    assert factor == pytest.approx(0.70)


def test_product_without_market_access_configuration_is_unaffected():
    product = pd.Series(
        {
            "product_id": "P001",
        }
    )

    factor = calculate_market_access_factor(
        product_row=product,
        month_start=pd.Timestamp("2024-06-01"),
    )

    assert factor == pytest.approx(1.0)
