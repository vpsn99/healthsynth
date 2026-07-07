from pathlib import Path

import pandas as pd


def validate_datasets(
    datasets: dict[str, pd.DataFrame],
    years: int = 3,
    output_dir: str = "output",
) -> Path:
    report_lines = []

    hcp_master = datasets["hcp_master"]
    product = datasets["product"]
    call_activity = datasets["call_activity"]
    prescriptions = datasets["prescriptions"]

    report_lines.append("# HealthSynth Validation Report")
    report_lines.append("")
    report_lines.append("## Table Counts")
    report_lines.append("")
    report_lines.append(f"- hcp_master: {len(hcp_master):,}")
    report_lines.append(f"- product: {len(product):,}")
    report_lines.append(f"- call_activity: {len(call_activity):,}")
    report_lines.append(f"- prescriptions: {len(prescriptions):,}")
    report_lines.append("")

    checks = []

    valid_hcps = set(hcp_master["hcp_id"])
    valid_products = set(product["product_id"])

    checks.append(
        (
            "Call activity HCP references are valid",
            set(call_activity["hcp_id"]).issubset(valid_hcps),
        )
    )

    checks.append(
        (
            "Prescription HCP references are valid",
            set(prescriptions["hcp_id"]).issubset(valid_hcps),
        )
    )

    checks.append(
        (
            "Call activity product references are valid",
            set(call_activity["product_id"]).issubset(valid_products),
        )
    )

    checks.append(
        (
            "Prescription product references are valid",
            set(prescriptions["product_id"]).issubset(valid_products),
        )
    )

    expected_rx_rows = len(hcp_master) * years * 12
    checks.append(
        (
            f"Prescription row count matches HCPs x {years * 12} months",
            len(prescriptions) == expected_rx_rows,
        )
    )

    launch_curve_ok = _check_launch_curve(prescriptions)
    checks.append(
        (
            "Launch curve shows higher later-period NRx than early-period NRx",
            launch_curve_ok,
        )
    )

    report_lines.append("## Checks")
    report_lines.append("")

    for check_name, passed in checks:
        symbol = "✅" if passed else "❌"
        report_lines.append(f"- {symbol} {check_name}")

    report_lines.append("")
    report_lines.append("## Notes")
    report_lines.append("")
    report_lines.append(
        "This report validates structural integrity and basic business behaviour. "
        "It does not imply medical or statistical validation."
    )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_path = output_path / "validation_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return report_path


def _check_launch_curve(prescriptions: pd.DataFrame) -> bool:
    rx = prescriptions.copy()
    rx["rx_date"] = pd.to_datetime(rx["rx_date"])

    monthly = rx.groupby(rx["rx_date"].dt.to_period("M"))["nrx"].sum().sort_index()

    if len(monthly) < 12:
        return False

    early_avg = monthly.iloc[:6].mean()
    late_avg = monthly.iloc[-6:].mean()

    return late_avg > early_avg
