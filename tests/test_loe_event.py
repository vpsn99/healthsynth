import pandas as pd
import pytest

from healthsynth.commercial.events.loe import calculate_loe_factor


@pytest.fixture
def loe_product():
    return pd.Series(
        {
            "product_id": "P001",
            "loe_date": "2024-01-01",
            "loe_erosion_months": 8,
            "post_loe_share_factor": 0.30,
        }
    )


def test_loe_factor_is_one_before_loe(loe_product):
    factor = calculate_loe_factor(
        product_row=loe_product,
        month_start=pd.Timestamp("2023-12-01"),
    )

    assert factor == pytest.approx(1.0)


def test_loe_factor_starts_at_one_in_loe_month(loe_product):
    factor = calculate_loe_factor(
        product_row=loe_product,
        month_start=pd.Timestamp("2024-01-01"),
    )

    assert factor == pytest.approx(1.0)


def test_loe_factor_declines_after_loe(loe_product):
    factor = calculate_loe_factor(
        product_row=loe_product,
        month_start=pd.Timestamp("2024-05-01"),
    )

    assert factor == pytest.approx(0.65)


def test_loe_factor_reaches_configured_floor(loe_product):
    factor = calculate_loe_factor(
        product_row=loe_product,
        month_start=pd.Timestamp("2024-09-01"),
    )

    assert factor == pytest.approx(0.30)


def test_product_without_loe_configuration_is_unaffected():
    product = pd.Series(
        {
            "product_id": "P002",
        }
    )

    factor = calculate_loe_factor(
        product_row=product,
        month_start=pd.Timestamp("2024-09-01"),
    )

    assert factor == pytest.approx(1.0)
