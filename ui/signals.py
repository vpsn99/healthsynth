from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MarketSignals:
    """Reusable commercial signals derived from monthly simulation data."""

    months_from_event: int | None
    largest_gainer: str | None
    largest_gain: float | None
    largest_loser: str | None
    largest_loss: float | None
    demand_change_pct: float | None
    leader_changed: bool


def extract_market_signals(
    *,
    current_month: pd.Timestamp,
    event_date: pd.Timestamp | None,
    current_share: pd.DataFrame,
    previous_share: pd.DataFrame | None,
    current_demand: int,
    previous_demand: int | None,
) -> MarketSignals:
    """Derive reusable commercial signals for one simulation month."""

    share_changes = _calculate_share_changes(
        current_share=current_share,
        previous_share=previous_share,
    )

    largest_gainer = _largest_change(
        share_changes,
        ascending=False,
    )

    largest_loser = _largest_change(
        share_changes,
        ascending=True,
    )

    demand_change_pct = _calculate_percentage_change(
        current_value=current_demand,
        previous_value=previous_demand,
    )

    current_leader = _market_leader(current_share)
    previous_leader = _market_leader(previous_share)

    return MarketSignals(
        months_from_event=_months_from_event(
            current_month=current_month,
            event_date=event_date,
        ),
        largest_gainer=(largest_gainer[0] if largest_gainer is not None else None),
        largest_gain=(largest_gainer[1] if largest_gainer is not None else None),
        largest_loser=(largest_loser[0] if largest_loser is not None else None),
        largest_loss=(largest_loser[1] if largest_loser is not None else None),
        demand_change_pct=demand_change_pct,
        leader_changed=(
            current_leader is not None
            and previous_leader is not None
            and current_leader != previous_leader
        ),
    )


def _calculate_share_changes(
    *,
    current_share: pd.DataFrame,
    previous_share: pd.DataFrame | None,
) -> pd.DataFrame:
    """Calculate product-level market-share change."""

    required_columns = {
        "product_name",
        "adjusted_market_share",
    }

    if not required_columns.issubset(current_share.columns):
        return pd.DataFrame()

    current = current_share[
        [
            "product_name",
            "adjusted_market_share",
        ]
    ].rename(
        columns={
            "adjusted_market_share": "current_share",
        }
    )

    if previous_share is None or previous_share.empty:
        current["previous_share"] = pd.NA
        current["share_change"] = pd.NA
        return current

    if not required_columns.issubset(previous_share.columns):
        current["previous_share"] = pd.NA
        current["share_change"] = pd.NA
        return current

    previous = previous_share[
        [
            "product_name",
            "adjusted_market_share",
        ]
    ].rename(
        columns={
            "adjusted_market_share": "previous_share",
        }
    )

    comparison = current.merge(
        previous,
        on="product_name",
        how="left",
    )

    comparison["share_change"] = comparison["current_share"] - comparison["previous_share"]

    return comparison


def _calculate_percentage_change(
    *,
    current_value: int,
    previous_value: int | None,
) -> float | None:
    """Calculate percentage change while handling missing baselines."""

    if previous_value is None or previous_value == 0:
        return None

    return (current_value - previous_value) / previous_value


def _largest_change(
    share_changes: pd.DataFrame,
    *,
    ascending: bool,
) -> tuple[str, float] | None:
    """Return the product with the largest share movement."""

    if share_changes.empty or "share_change" not in share_changes.columns:
        return None

    valid_changes = share_changes.dropna(subset=["share_change"])

    if valid_changes.empty:
        return None

    row = valid_changes.sort_values(
        "share_change",
        ascending=ascending,
    ).iloc[0]

    return (
        str(row["product_name"]),
        float(row["share_change"]),
    )


def _months_from_event(
    *,
    current_month: pd.Timestamp,
    event_date: pd.Timestamp | None,
) -> int | None:
    """Return the number of months before or after the event."""

    if event_date is None:
        return None

    return (current_month.year - event_date.year) * 12 + (current_month.month - event_date.month)


def _market_leader(
    share_data: pd.DataFrame | None,
) -> str | None:
    """Return the product with the highest adjusted market share."""

    if share_data is None or share_data.empty:
        return None

    required_columns = {
        "product_name",
        "adjusted_market_share",
    }

    if not required_columns.issubset(share_data.columns):
        return None

    leader = share_data.sort_values(
        "adjusted_market_share",
        ascending=False,
    ).iloc[0]

    return str(leader["product_name"])
