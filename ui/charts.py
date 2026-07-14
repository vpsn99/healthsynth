from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


def find_scenario_event(
    products: pd.DataFrame | None,
    scenario_name: str,
) -> tuple[pd.Timestamp | None, str | None]:
    """Return the primary event date and label for a scenario."""

    if products is None or products.empty:
        return None, None

    if scenario_name == "Loss of Exclusivity":
        if "loe_date" not in products.columns:
            return None, None

        event_dates = pd.to_datetime(
            products["loe_date"],
            errors="coerce",
        ).dropna()

        if not event_dates.empty:
            return event_dates.min(), "Loss of exclusivity"

    if scenario_name == "Market Access":
        if "market_access_date" not in products.columns:
            return None, None

        event_dates = pd.to_datetime(
            products["market_access_date"],
            errors="coerce",
        ).dropna()

        if not event_dates.empty:
            return event_dates.min(), "Market access change"

    if scenario_name in {
        "New Product Launch",
        "Competitor Launch",
    }:
        if "launch_date" not in products.columns:
            return None, None

        launch_dates = pd.to_datetime(
            products["launch_date"],
            errors="coerce",
        ).dropna()

        if not launch_dates.empty:
            label = (
                "New product launch"
                if scenario_name == "New Product Launch"
                else "Competitor launch"
            )

            return launch_dates.max(), label

    return None, None


def show_market_share_chart(
    dataframes: dict[str, pd.DataFrame],
    scenario_name: str,
) -> None:
    """Display adjusted market share with event context."""

    market_share = dataframes.get("market_share")
    products = dataframes.get("product")

    if market_share is None or market_share.empty or products is None or products.empty:
        st.info("Market-share data is not available.")
        return

    required_columns = {
        "month",
        "product_id",
        "adjusted_market_share",
    }

    if not required_columns.issubset(market_share.columns):
        st.info("The market-share schema cannot be charted.")
        return

    chart_data = market_share.copy()
    chart_data["month"] = pd.to_datetime(chart_data["month"])

    if "product_name" in products.columns:
        chart_data = chart_data.merge(
            products[
                [
                    "product_id",
                    "product_name",
                ]
            ],
            on="product_id",
            how="left",
        )
        series_column = "product_name"
    else:
        series_column = "product_id"

    line_chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "month:T",
                title="Month",
            ),
            y=alt.Y(
                "adjusted_market_share:Q",
                title="Adjusted market share",
                axis=alt.Axis(format=".0%"),
            ),
            color=alt.Color(
                f"{series_column}:N",
                title="Product",
            ),
            tooltip=[
                alt.Tooltip(
                    "month:T",
                    title="Month",
                    format="%b %Y",
                ),
                alt.Tooltip(
                    f"{series_column}:N",
                    title="Product",
                ),
                alt.Tooltip(
                    "adjusted_market_share:Q",
                    title="Market share",
                    format=".2%",
                ),
            ],
        )
        .properties(height=420)
    )

    event_date, event_label = find_scenario_event(
        products=products,
        scenario_name=scenario_name,
    )

    if event_date is not None:
        event_data = pd.DataFrame(
            {
                "event_date": [event_date],
                "event_label": [event_label],
            }
        )

        event_rule = (
            alt.Chart(event_data)
            .mark_rule(
                strokeDash=[6, 4],
                strokeWidth=2,
            )
            .encode(
                x="event_date:T",
                tooltip=[
                    alt.Tooltip(
                        "event_date:T",
                        title="Event date",
                        format="%b %Y",
                    ),
                    alt.Tooltip(
                        "event_label:N",
                        title="Commercial event",
                    ),
                ],
            )
        )

        event_text = (
            alt.Chart(event_data)
            .mark_text(
                align="left",
                baseline="top",
                dx=6,
                dy=8,
            )
            .encode(
                x="event_date:T",
                text="event_label:N",
            )
        )

        final_chart = line_chart + event_rule + event_text
    else:
        final_chart = line_chart

    st.altair_chart(final_chart, width="stretch")


def show_market_demand_chart(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """Display monthly market demand."""

    market_demand = dataframes.get("market_demand")

    if market_demand is None or market_demand.empty:
        st.info("Market-demand data is not available.")
        return

    required_columns = {
        "month",
        "market_nrx",
    }

    if not required_columns.issubset(market_demand.columns):
        st.info("The market-demand schema cannot be charted.")
        return

    chart_data = market_demand.copy()
    chart_data["month"] = pd.to_datetime(chart_data["month"])

    monthly_demand = chart_data.groupby("month")["market_nrx"].sum().sort_index()

    st.line_chart(monthly_demand)


def show_prescription_chart(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """Display monthly NRx by product."""

    prescriptions = dataframes.get("prescriptions")
    products = dataframes.get("product")

    if prescriptions is None or prescriptions.empty:
        st.info("Prescription data is not available.")
        return

    required_columns = {
        "rx_date",
        "product_id",
        "nrx",
    }

    if not required_columns.issubset(prescriptions.columns):
        st.info("The prescription schema cannot be charted.")
        return

    chart_data = prescriptions.copy()
    chart_data["rx_date"] = pd.to_datetime(chart_data["rx_date"])

    if products is not None and not products.empty and "product_name" in products.columns:
        chart_data = chart_data.merge(
            products[
                [
                    "product_id",
                    "product_name",
                ]
            ],
            on="product_id",
            how="left",
        )
        series_column = "product_name"
    else:
        series_column = "product_id"

    monthly_rx = (
        chart_data.groupby(
            [
                "rx_date",
                series_column,
            ]
        )["nrx"]
        .sum()
        .reset_index()
        .pivot(
            index="rx_date",
            columns=series_column,
            values="nrx",
        )
    )

    st.line_chart(monthly_rx)
