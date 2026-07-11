import pandas as pd


def calculate_loe_factor(
    product_row: pd.Series,
    month_start: pd.Timestamp,
) -> float:
    """
    Calculate the product's competitive factor after loss of exclusivity.

    Before the LOE date, the product retains its full competitive
    potential and the factor is 1.0.

    After LOE, the factor declines linearly until it reaches the
    configured post-LOE floor.
    """
    loe_date_value = product_row.get("loe_date")

    if pd.isna(loe_date_value):
        return 1.0

    loe_date = pd.Timestamp(loe_date_value).to_period("M")
    simulation_month = month_start.to_period("M")

    months_since_loe = (
        (simulation_month.year - loe_date.year) * 12 + simulation_month.month - loe_date.month
    )

    if months_since_loe < 0:
        return 1.0

    erosion_months_value = product_row.get("loe_erosion_months")
    floor_factor_value = product_row.get("post_loe_share_factor")

    if pd.isna(erosion_months_value):
        return 1.0

    erosion_months = int(erosion_months_value)

    if erosion_months <= 0:
        return float(floor_factor_value)

    floor_factor = 0.30 if pd.isna(floor_factor_value) else float(floor_factor_value)

    progress = min(
        months_since_loe / erosion_months,
        1.0,
    )

    return 1.0 - ((1.0 - floor_factor) * progress)
