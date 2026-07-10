import pandas as pd


def build_simulation_months(
    start_date: str | pd.Timestamp,
    years: int,
) -> pd.DatetimeIndex:
    start = pd.Timestamp(start_date).to_period("M").to_timestamp()
    end = start + pd.DateOffset(years=years)

    return pd.date_range(
        start=start,
        end=end,
        freq="MS",
        inclusive="left",
    )
