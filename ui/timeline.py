from __future__ import annotations

import time

import pandas as pd
import streamlit as st
from charts import find_scenario_event


def show_timeline_explorer(
    dataframes: dict[str, pd.DataFrame],
    scenario_name: str,
) -> None:
    """Explore the simulated market one month at a time."""

    market_share = dataframes.get("market_share")
    market_demand = dataframes.get("market_demand")
    prescriptions = dataframes.get("prescriptions")
    products = dataframes.get("product")

    required_datasets = {
        "market_share": market_share,
        "market_demand": market_demand,
        "prescriptions": prescriptions,
        "product": products,
    }

    missing_datasets = [
        name
        for name, dataframe in required_datasets.items()
        if dataframe is None or dataframe.empty
    ]

    if missing_datasets:
        st.info("Timeline playback requires: " + ", ".join(missing_datasets))
        return

    share_data = market_share.copy()
    demand_data = market_demand.copy()
    prescription_data = prescriptions.copy()

    share_data["month"] = pd.to_datetime(share_data["month"])
    demand_data["month"] = pd.to_datetime(demand_data["month"])
    prescription_data["rx_date"] = pd.to_datetime(prescription_data["rx_date"])

    product_lookup = products[
        [
            "product_id",
            "product_name",
        ]
    ].drop_duplicates()

    share_data = share_data.merge(
        product_lookup,
        on="product_id",
        how="left",
    )

    prescription_data = prescription_data.merge(
        product_lookup,
        on="product_id",
        how="left",
    )

    available_months = sorted(share_data["month"].dropna().unique())

    if not available_months:
        st.info("No simulation months are available.")
        return

    timeline_key = "timeline_month_index"
    playing_key = "timeline_playing"

    if timeline_key not in st.session_state:
        st.session_state[timeline_key] = 0

    if playing_key not in st.session_state:
        st.session_state[playing_key] = False

    maximum_index = len(available_months) - 1

    st.session_state[timeline_key] = min(
        st.session_state[timeline_key],
        maximum_index,
    )

    event_date, event_label = find_scenario_event(
        products=products,
        scenario_name=scenario_name,
    )

    event_index = None

    if event_date is not None:
        event_month = event_date.to_period("M")

        for index, month in enumerate(available_months):
            if pd.Timestamp(month).to_period("M") == event_month:
                event_index = index
                break

    (
        previous_column,
        play_column,
        next_column,
        event_column,
    ) = st.columns([1, 1, 1, 1])

    with previous_column:
        if st.button(
            "◀ Previous",
            width="stretch",
            disabled=(st.session_state[timeline_key] == 0),
        ):
            st.session_state[timeline_key] -= 1
            st.session_state[playing_key] = False
            st.rerun()

    with play_column:
        play_label = "⏸ Pause" if st.session_state[playing_key] else "▶ Play"

        if st.button(
            play_label,
            width="stretch",
        ):
            st.session_state[playing_key] = not st.session_state[playing_key]
            st.rerun()

    with next_column:
        if st.button(
            "Next ▶",
            width="stretch",
            disabled=(st.session_state[timeline_key] == maximum_index),
        ):
            st.session_state[timeline_key] += 1
            st.session_state[playing_key] = False
            st.rerun()

    with event_column:
        event_button_label = f"Jump to {event_label}" if event_label is not None else "No event"

        if st.button(
            event_button_label,
            width="stretch",
            disabled=event_index is None,
        ):
            st.session_state[timeline_key] = event_index
            st.session_state[playing_key] = False
            st.rerun()

    selected_index = st.slider(
        "Simulation month",
        min_value=0,
        max_value=maximum_index,
        value=st.session_state[timeline_key],
        format="Month %d",
    )

    if selected_index != st.session_state[timeline_key]:
        st.session_state[timeline_key] = selected_index
        st.session_state[playing_key] = False

    current_month = pd.Timestamp(available_months[st.session_state[timeline_key]])

    st.markdown(f"## {current_month:%B %Y}")

    if event_date is not None:
        event_month = event_date.to_period("M")

        for index, month in enumerate(available_months):
            if pd.Timestamp(month).to_period("M") == event_month:
                event_index = index
                break

    if event_date is not None and current_month.to_period("M") == event_date.to_period("M"):
        st.warning(f"Commercial event: **{event_label}**")

    current_share = share_data[share_data["month"] == current_month].copy()

    current_demand_rows = demand_data[demand_data["month"] == current_month]

    current_prescriptions = prescription_data[prescription_data["rx_date"] == current_month]

    total_market_nrx = int(current_demand_rows["market_nrx"].sum())

    monthly_product_nrx = (
        current_prescriptions.groupby(
            "product_name",
            as_index=False,
        )["nrx"]
        .sum()
        .sort_values(
            "nrx",
            ascending=False,
        )
    )

    current_share = current_share.sort_values(
        "adjusted_market_share",
        ascending=False,
    )

    market_leader = (
        current_share.iloc[0]["product_name"] if not current_share.empty else "Not available"
    )

    leader_share = (
        float(current_share.iloc[0]["adjusted_market_share"]) if not current_share.empty else 0.0
    )

    top_nrx_product = (
        monthly_product_nrx.iloc[0]["product_name"]
        if not monthly_product_nrx.empty
        else "Not available"
    )

    summary_columns = st.columns(4)

    summary_columns[0].metric(
        "Current month",
        current_month.strftime("%b %Y"),
    )

    summary_columns[1].metric(
        "Market demand",
        f"{total_market_nrx:,} NRx",
    )

    summary_columns[2].metric(
        "Market leader",
        market_leader,
        f"{leader_share:.1%} share",
    )

    summary_columns[3].metric(
        "Top NRx product",
        top_nrx_product,
    )

    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.markdown("#### Market Share")

        share_chart_data = current_share.set_index("product_name")["adjusted_market_share"]

        st.bar_chart(
            share_chart_data,
            horizontal=True,
        )

    with right_chart:
        st.markdown("#### New Prescriptions")

        nrx_chart_data = monthly_product_nrx.set_index("product_name")["nrx"]

        st.bar_chart(
            nrx_chart_data,
            horizontal=True,
        )

    st.markdown("#### Monthly Product Position")

    monthly_position = current_share[
        [
            "product_name",
            "adjusted_market_share",
        ]
    ].merge(
        monthly_product_nrx,
        on="product_name",
        how="left",
    )

    monthly_position["nrx"] = monthly_position["nrx"].fillna(0).astype(int)

    monthly_position["adjusted_market_share"] = monthly_position["adjusted_market_share"].map(
        lambda value: f"{value:.2%}"
    )

    monthly_position = monthly_position.rename(
        columns={
            "product_name": "Product",
            "adjusted_market_share": "Market Share",
            "nrx": "NRx",
        }
    )

    st.dataframe(
        monthly_position,
        hide_index=True,
        width="stretch",
    )

    if st.session_state[playing_key]:
        if st.session_state[timeline_key] < maximum_index:
            time.sleep(0.8)
            st.session_state[timeline_key] += 1
            st.rerun()
        else:
            st.session_state[playing_key] = False
            st.success("Timeline playback completed.")
