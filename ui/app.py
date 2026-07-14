from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

from healthsynth import generate

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPOSITORY_ROOT / "output" / "ui"

SCENARIOS = {
    "Default Market": None,
    "Oncology Training": (
        REPOSITORY_ROOT
        / "configs"
        / "profiles"
        / "oncology_training.yaml"
    ),
    "New Product Launch": (
        REPOSITORY_ROOT
        / "configs"
        / "profiles"
        / "oncology_product_launch.yaml"
    ),
    "Loss of Exclusivity": (
        REPOSITORY_ROOT
        / "configs"
        / "profiles"
        / "oncology_loe.yaml"
    ),
    "Competitor Launch": (
        REPOSITORY_ROOT
        / "configs"
        / "profiles"
        / "oncology_competitor_launch.yaml"
    ),
    "Market Access": (
        REPOSITORY_ROOT
        / "configs"
        / "profiles"
        / "oncology_market_access.yaml"
    ),
}


def dataframe_results(results: dict) -> dict[str, pd.DataFrame]:
    """Return only DataFrame objects from the simulation result."""

    return {
        name: value
        for name, value in results.items()
        if isinstance(value, pd.DataFrame)
    }


def build_output_zip(output_dir: Path) -> bytes:
    """Create an in-memory ZIP containing one simulation run."""

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                archive.write(
                    file_path,
                    arcname=file_path.relative_to(output_dir),
                )

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


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


def show_market_share_chart(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """Display adjusted market share by product and month."""

    market_share = dataframes.get("market_share")
    products = dataframes.get("product")

    if (
        market_share is None
        or market_share.empty
        or products is None
        or products.empty
    ):
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

    market_share_pivot = chart_data.pivot(
        index="month",
        columns=series_column,
        values="adjusted_market_share",
    )

    st.line_chart(market_share_pivot)


def show_market_demand_chart(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """Display monthly market demand."""

    market_demand = dataframes.get("market_demand")

    if market_demand is None or market_demand.empty:
        st.info("Market-demand data is not available.")
        return

    if not {"month", "market_nrx"}.issubset(
        market_demand.columns
    ):
        st.info("The market-demand schema cannot be charted.")
        return

    chart_data = market_demand.copy()
    chart_data["month"] = pd.to_datetime(chart_data["month"])

    monthly_demand = (
        chart_data.groupby("month")["market_nrx"]
        .sum()
        .sort_index()
    )

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

    if not required_columns.issubset(
        prescriptions.columns
    ):
        st.info("The prescription schema cannot be charted.")
        return

    chart_data = prescriptions.copy()
    chart_data["rx_date"] = pd.to_datetime(
        chart_data["rx_date"]
    )

    if (
        products is not None
        and not products.empty
        and "product_name" in products.columns
    ):
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

    st.caption(
        f"{len(selected_dataset):,} rows × "
        f"{len(selected_dataset.columns):,} columns"
    )

    st.dataframe(
        selected_dataset.head(250),
        use_container_width=True,
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

    validation_text = validation_path.read_text(
        encoding="utf-8"
    )

    st.markdown(validation_text)


st.set_page_config(
    page_title="HealthSynth",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 HealthSynth")
st.subheader("Build and explore a pharmaceutical commercial market")

st.caption(
    "Choose a commercial scenario, run the simulation, "
    "and explore the market dynamics that emerge."
)

with st.sidebar:
    st.header("Build Your Market")

    scenario_name = st.selectbox(
        "Commercial scenario",
        options=list(SCENARIOS),
        index=1,
    )

    scenario_path = SCENARIOS[scenario_name]

    if scenario_path is not None:
        if scenario_path.exists():
            st.caption(scenario_path.name)
        else:
            st.error(
                f"Profile not found: {scenario_path.name}"
            )

    st.divider()

    hcps = st.number_input(
        "Healthcare providers",
        min_value=10,
        max_value=10_000,
        value=100,
        step=10,
        help=(
            "Number of healthcare providers in the "
            "simulated market."
        ),
    )

    years = st.number_input(
        "Simulation years",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    seed = st.number_input(
        "Random seed",
        min_value=0,
        value=42,
        step=1,
        help=(
            "Use the same seed to reproduce the same "
            "simulation."
        ),
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

    st.divider()

    run_simulation = st.button(
        "Run Simulation",
        type="primary",
        use_container_width=True,
        disabled=(
            scenario_path is not None
            and not scenario_path.exists()
        ),
    )

if run_simulation:
    run_id = time.strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_ROOT / run_id

    generation_arguments = {
        "hcps": int(hcps),
        "years": int(years),
        "seed": int(seed),
        "output_dir": str(output_dir),
        "output_format": output_format,
    }

    if scenario_path is not None:
        generation_arguments["config_path"] = str(
            scenario_path
        )

    try:
        with st.spinner(
            f"Simulating: {scenario_name}..."
        ):
            results = generate(**generation_arguments)

        st.session_state["simulation_results"] = results
        st.session_state["simulation_output_dir"] = output_dir
        st.session_state["simulation_scenario"] = scenario_name

    except Exception as exc:
        st.error("The simulation could not be completed.")
        st.exception(exc)

if "simulation_results" not in st.session_state:
    st.info(
        "Choose a scenario and simulation settings in the "
        "sidebar, then select **Run Simulation**."
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

results = st.session_state["simulation_results"]
output_dir = st.session_state["simulation_output_dir"]
scenario_name = st.session_state["simulation_scenario"]

dataframes = dataframe_results(results)

st.success(
    f"Simulation completed: **{scenario_name}**"
)

show_summary(dataframes)

overview_tab, charts_tab, data_tab, validation_tab = st.tabs(
    [
        "Overview",
        "Market Dynamics",
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
                use_container_width=True,
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
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No product data is available.")

with charts_tab:
    st.subheader("Market Dynamics")

    st.markdown("#### Adjusted Market Share")
    show_market_share_chart(dataframes)

    st.markdown("#### Monthly Market Demand")
    show_market_demand_chart(dataframes)

    st.markdown("#### Monthly New Prescriptions")
    show_prescription_chart(dataframes)

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
        file_name=(
            f"healthsynth_{scenario_name.lower().replace(' ', '_')}"
            f"_{output_dir.name}.zip"
        ),
        mime="application/zip",
        use_container_width=True,
    )

    st.caption(
        f"Output directory: `{output_dir}`"
    )