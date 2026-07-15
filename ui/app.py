from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from charts import (
    show_market_demand_chart,
    show_market_share_chart,
    show_prescription_chart,
)
from models import SimulationSession, SimulationSettings
from scenarios import build_scenarios
from services import (
    build_output_zip,
    run_simulation,
    validate_simulation_inputs,
)
from timeline import show_timeline_explorer

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPOSITORY_ROOT / "output" / "ui"

SCENARIOS = build_scenarios(REPOSITORY_ROOT)


def show_summary(dataframes: dict[str, pd.DataFrame]) -> None:
    """Display top-level simulation metrics."""

    metrics = [
        (
            "Markets",
            len(dataframes.get("market", pd.DataFrame())),
        ),
        (
            "Products",
            len(dataframes.get("product", pd.DataFrame())),
        ),
        (
            "HCPs",
            len(dataframes.get("hcp_master", pd.DataFrame())),
        ),
        (
            "Promotional Calls",
            len(dataframes.get("call_activity", pd.DataFrame())),
        ),
        (
            "Prescription Rows",
            len(dataframes.get("prescriptions", pd.DataFrame())),
        ),
    ]

    columns = st.columns(len(metrics))

    for column, (label, value) in zip(
        columns,
        metrics,
        strict=True,
    ):
        column.metric(label, f"{value:,}")


def show_dataset_preview(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """Allow the user to inspect generated datasets."""

    if not dataframes:
        st.warning("No tabular datasets were returned.")
        return

    dataset_name = st.selectbox(
        "Dataset",
        options=sorted(dataframes),
    )

    selected_dataset = dataframes[dataset_name]

    st.caption(f"{len(selected_dataset):,} rows × {len(selected_dataset.columns):,} columns")

    st.dataframe(
        selected_dataset.head(250),
        width="stretch",
        hide_index=True,
    )

    if len(selected_dataset) > 250:
        st.caption("Showing the first 250 rows.")


def show_validation_report(output_dir: Path) -> None:
    """Display the generated validation report."""

    validation_path = output_dir / "validation_report.md"

    if not validation_path.exists():
        st.info("No validation report was generated.")
        return

    validation_text = validation_path.read_text(encoding="utf-8")

    st.markdown(validation_text)


st.set_page_config(
    page_title="HealthSynth Studio",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 HealthSynth Studio")
st.subheader("Interactive pharmaceutical commercial market simulator")

st.caption(
    "Powered by HealthSynth Core. Choose a commercial scenario, "
    "run the simulation, and explore how the market evolves."
)

with st.sidebar:
    st.header("Build Your Market")

    scenario_name = st.selectbox(
        "Commercial scenario",
        options=list(SCENARIOS),
        index=1,
    )

    scenario = SCENARIOS[scenario_name]
    scenario_path = scenario["path"]

    st.markdown(f"**{scenario['title']}**")
    st.caption(scenario["description"])

    with st.expander("Commercial question"):
        st.write(scenario["question"])

    if scenario_path is not None:
        if scenario_path.exists():
            st.caption(f"Profile: `{scenario_path.name}`")
        else:
            st.error(f"The profile file could not be found: `{scenario_path.name}`")

    st.divider()

    hcps = st.number_input(
        "Healthcare providers",
        min_value=10,
        max_value=5_000,
        value=100,
        step=10,
        help=(
            "Controls the size of the simulated HCP population. "
            "Start with 100 for a quick demonstration."
        ),
    )

    years = st.number_input(
        "Simulation years",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
        help=("Commercial scenario profiles are designed primarily for a three-year simulation."),
    )

    estimated_prescription_rows = int(hcps) * 3 * int(years) * 12

    st.caption(f"Estimated prescription rows: **{estimated_prescription_rows:,}**")

    if estimated_prescription_rows > 300_000:
        st.warning(
            "This is a relatively large simulation and may take "
            "several minutes. Consider reducing the HCP count for "
            "an interactive demonstration."
        )

    seed = st.number_input(
        "Random seed",
        min_value=0,
        value=42,
        step=1,
        help=("Use the same seed to reproduce the same simulation."),
    )

    output_format = st.selectbox(
        "Output format",
        options=[
            "csv",
            "duckdb",
            "all",
        ],
        index=2,
    )

    simulation_settings = SimulationSettings(
        scenario_name=scenario_name,
        scenario_path=scenario_path,
        hcps=int(hcps),
        years=int(years),
        seed=int(seed),
        output_format=output_format,
    )

    st.divider()

    run_simulation_requested = st.button(
        "🧬 Run Simulation",
        type="primary",
        width="stretch",
        disabled=(scenario_path is not None and not scenario_path.exists()),
    )

    if run_simulation_requested:
        input_errors = validate_simulation_inputs(simulation_settings)

        if input_errors:
            for error in input_errors:
                st.error(error)

            st.stop()

        try:
            with st.spinner(f"Simulating: {scenario_name}..."):
                simulation_session = run_simulation(
                    settings=simulation_settings,
                    output_root=OUTPUT_ROOT,
                )

            st.session_state["simulation_session"] = simulation_session

            st.session_state["timeline_month_index"] = 0
            st.session_state["timeline_playing"] = False

        except FileNotFoundError as exc:
            st.error("The selected configuration file could not be found.")
            st.code(str(exc))

        except ValueError as exc:
            st.error("The simulation configuration is not valid.")
            st.code(str(exc))

        except Exception as exc:
            st.error("HealthSynth encountered an unexpected error while running the simulation.")

            with st.expander("Technical details"):
                st.exception(exc)

if "simulation_session" not in st.session_state:
    st.info(
        "Choose a scenario and simulation settings in the sidebar, then select **Run Simulation**."
    )

    st.markdown(
        """
### What can you simulate?

- A new oncology product entering the market
- Loss of exclusivity for an established product
- The launch of a new competitor
- Improved or restricted market access
- A standard training market for exploratory analytics
"""
    )

    st.stop()

simulation_session: SimulationSession = st.session_state["simulation_session"]

scenario_name = simulation_session.scenario_name
output_dir = simulation_session.output_dir
dataframes = simulation_session.dataframes

st.success(f"Simulation completed: **{scenario_name}**")

show_summary(dataframes)

(
    overview_tab,
    charts_tab,
    timeline_tab,
    data_tab,
    validation_tab,
) = st.tabs(
    [
        "Overview",
        "Market Dynamics",
        "Timeline",
        "Datasets",
        "Validation & Download",
    ]
)

with overview_tab:
    st.subheader("Simulation Overview")

    market = dataframes.get("market")
    products = dataframes.get("product")

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown("#### Market")

        if market is not None and not market.empty:
            st.dataframe(
                market,
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No market summary is available.")

    with right_column:
        st.markdown("#### Product Portfolio")

        if products is not None and not products.empty:
            product_columns = [
                column
                for column in [
                    "product_id",
                    "product_name",
                    "manufacturer",
                    "brand_type",
                    "launch_date",
                    "baseline_market_share",
                ]
                if column in products.columns
            ]

            st.dataframe(
                products[product_columns],
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No product data is available.")

    with charts_tab:
        st.subheader("Market Dynamics")

        st.markdown("#### Adjusted Market Share")
        show_market_share_chart(
            dataframes=dataframes,
            scenario_name=scenario_name,
        )

        if scenario_name == "New Product Launch":
            st.caption(
                "Observe how the newly launched product gradually gains "
                "share from established competitors."
            )
        elif scenario_name == "Loss of Exclusivity":
            st.caption(
                "Observe how the affected brand loses competitive "
                "strength after loss of exclusivity."
            )
        elif scenario_name == "Competitor Launch":
            st.caption(
                "Observe how the new competitor enters the market and "
                "redistributes share away from incumbents."
            )
        elif scenario_name == "Market Access":
            st.caption(
                "Observe how improved access changes the product's "
                "competitive position after the event date."
            )
        else:
            st.caption(
                "Market share changes over time as products compete within the simulated market."
            )

        st.markdown("#### Monthly Market Demand")
        show_market_demand_chart(dataframes)

        st.markdown("#### Monthly New Prescriptions")
        show_prescription_chart(dataframes)

    with timeline_tab:
        st.subheader("Market Timeline")

        st.caption(
            "Move through the simulation month by month, or select Play to watch the market evolve."
        )

        show_timeline_explorer(
            dataframes=dataframes,
            scenario_name=scenario_name,
        )

with data_tab:
    st.subheader("Generated Datasets")
    show_dataset_preview(dataframes)

with validation_tab:
    st.subheader("Validation Report")
    show_validation_report(output_dir)

    st.divider()

    st.subheader("Download Simulation")

    zip_bytes = build_output_zip(output_dir)

    st.download_button(
        label="Download Simulation as ZIP",
        data=zip_bytes,
        file_name=(f"healthsynth_{scenario_name.lower().replace(' ', '_')}_{output_dir.name}.zip"),
        mime="application/zip",
        width="stretch",
    )

    st.caption(f"Output directory: `{output_dir}`")
