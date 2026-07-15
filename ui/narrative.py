from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from signals import MarketSignals, extract_market_signals


@dataclass(frozen=True)
class MarketNarrative:
    """Compact commercial interpretation for one simulation month."""

    phase: str
    summary: str
    details: tuple[str, ...]


def build_market_narrative(
    *,
    scenario_name: str,
    current_month: pd.Timestamp,
    event_date: pd.Timestamp | None,
    current_share: pd.DataFrame,
    previous_share: pd.DataFrame | None,
    current_demand: int,
    previous_demand: int | None,
) -> MarketNarrative:
    """Build a short, deterministic commercial narrative."""

    signals = extract_market_signals(
        current_month=current_month,
        event_date=event_date,
        current_share=current_share,
        previous_share=previous_share,
        current_demand=current_demand,
        previous_demand=previous_demand,
    )

    phase = _determine_phase(
        scenario_name=scenario_name,
        months_from_event=signals.months_from_event,
    )

    summary = _build_summary(
        scenario_name=scenario_name,
        phase=phase,
        signals=signals,
    )

    details = _build_details(
        signals=signals,
    )

    return MarketNarrative(
        phase=phase,
        summary=summary,
        details=details,
    )


def _determine_phase(
    *,
    scenario_name: str,
    months_from_event: int | None,
) -> str:
    """Return a short phase label for the current simulation month."""

    if months_from_event is None:
        return "Market observation"

    if months_from_event < 0:
        return "Pre-event"

    if months_from_event == 0:
        return _event_phase_name(scenario_name)

    if months_from_event <= 3:
        return "Early response"

    if months_from_event <= 9:
        return "Market adjustment"

    return "Post-event market"


def _event_phase_name(scenario_name: str) -> str:
    """Return the scenario-specific event phase label."""

    labels = {
        "New Product Launch": "Launch month",
        "Competitor Launch": "Competitor entry",
        "Loss of Exclusivity": "Loss of exclusivity",
        "Market Access": "Access change",
    }

    return labels.get(
        scenario_name,
        "Commercial event",
    )


def _build_summary(
    *,
    scenario_name: str,
    phase: str,
    signals: MarketSignals,
) -> str:
    """Build the always-visible one-line narrative."""

    demand_description = _describe_demand(signals.demand_change_pct)

    if phase == "Pre-event":
        return (
            "The market remains in its pre-event state, with "
            "incumbent products maintaining their established positions."
        )

    if phase in {
        "Launch month",
        "Competitor entry",
        "Loss of exclusivity",
        "Access change",
    }:
        return _event_month_summary(
            scenario_name=scenario_name,
            demand_description=demand_description,
        )

    if (
        signals.largest_gainer is not None
        and signals.largest_gain is not None
        and signals.largest_gain > 0
    ):
        return (
            f"{signals.largest_gainer} gained "
            f"{signals.largest_gain:.1%} share versus the previous "
            f"month while {demand_description}."
        )

    if signals.leader_changed:
        return f"The market leader changed this month while {demand_description}."

    return f"Market positions remain broadly stable while {demand_description}."


def _event_month_summary(
    *,
    scenario_name: str,
    demand_description: str,
) -> str:
    """Return a scenario-specific event-month summary."""

    summaries = {
        "New Product Launch": (
            "A new product enters the market this month; early adoption "
            f"begins while {demand_description}."
        ),
        "Competitor Launch": (
            "A new competitor enters the market and begins challenging "
            f"incumbent products while {demand_description}."
        ),
        "Loss of Exclusivity": (
            "Loss of exclusivity begins to weaken the established "
            f"product's position while {demand_description}."
        ),
        "Market Access": (
            "The access change alters the product's competitive "
            f"opportunity while {demand_description}."
        ),
    }

    return summaries.get(
        scenario_name,
        f"A commercial event occurs this month while {demand_description}.",
    )


def _build_details(
    *,
    signals: MarketSignals,
) -> tuple[str, ...]:
    """Build up to three expandable supporting observations."""

    details: list[str] = []

    if (
        signals.largest_gainer is not None
        and signals.largest_gain is not None
        and signals.largest_gain > 0
    ):
        details.append(
            f"{signals.largest_gainer} recorded the largest "
            f"monthly share gain at {signals.largest_gain:.1%}."
        )

    if (
        signals.largest_loser is not None
        and signals.largest_loss is not None
        and signals.largest_loss < 0
    ):
        details.append(
            f"{signals.largest_loser} recorded the largest "
            f"monthly share decline at "
            f"{abs(signals.largest_loss):.1%}."
        )

    if signals.leader_changed:
        details.append("The market leader changed compared with the previous month.")

    demand_change_pct = signals.demand_change_pct

    if demand_change_pct is not None:
        if abs(demand_change_pct) < 0.01:
            details.append(
                "Total market demand remained broadly stable, so "
                "product movement mainly reflects share redistribution."
            )
        elif demand_change_pct > 0:
            details.append(
                f"Total market demand increased by "
                f"{demand_change_pct:.1%} versus the previous month."
            )
        else:
            details.append(
                f"Total market demand decreased by "
                f"{abs(demand_change_pct):.1%} versus the previous month."
            )

    return tuple(details[:3])


def _describe_demand(
    demand_change_pct: float | None,
) -> str:
    """Return concise wording for monthly market-demand movement."""

    if demand_change_pct is None:
        return "market demand has no prior-month comparison"

    if abs(demand_change_pct) < 0.01:
        return "total market demand remains broadly stable"

    if demand_change_pct > 0:
        return "total market demand is increasing"

    return "total market demand is declining"
