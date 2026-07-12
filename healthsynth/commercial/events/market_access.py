import pandas as pd


def calculate_market_access_factor(
    product_row: pd.Series,
    month_start: pd.Timestamp,
) -> float:
    """
    Return the product's market-access factor for a simulation month.

    Before the configured access date, the product retains its normal
    competitive strength with a factor of 1.0.

    From the access date onward, the configured factor is applied.
    Values above 1.0 represent improved access, while values below 1.0
    represent restricted access.
    """
    access_date_value = product_row.get("market_access_date")
    access_factor_value = product_row.get("market_access_factor")

    if pd.isna(access_date_value):
        return 1.0

    access_date = pd.Timestamp(access_date_value).to_period("M")

    simulation_month = month_start.to_period("M")

    if simulation_month < access_date:
        return 1.0

    if pd.isna(access_factor_value):
        return 1.0

    return float(access_factor_value)
