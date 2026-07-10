import pandas as pd

from healthsynth.simulation.calendar import build_simulation_months


def test_build_simulation_months_returns_expected_range():
    months = build_simulation_months(
        start_date="2024-03-01",
        years=1,
    )

    assert len(months) == 12
    assert months[0] == pd.Timestamp("2024-03-01")
    assert months[-1] == pd.Timestamp("2025-02-01")


def test_build_simulation_months_normalizes_to_month_start():
    months = build_simulation_months(
        start_date="2024-03-15",
        years=1,
    )

    assert months[0] == pd.Timestamp("2024-03-01")
