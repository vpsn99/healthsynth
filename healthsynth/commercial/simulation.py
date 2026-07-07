from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from healthsynth.commercial.entities import generate_hcps, generate_products
from healthsynth.commercial.facts import generate_call_activity, generate_prescriptions
from healthsynth.config import DEFAULT_COMMERCIAL_CONFIG
from healthsynth.exporters.duckdb_exporter import write_duckdb


@dataclass
class CommercialSimulationResult:
    hcp_master: pd.DataFrame
    product: pd.DataFrame
    call_activity: pd.DataFrame
    prescriptions: pd.DataFrame

    def as_dict(self) -> dict[str, pd.DataFrame]:
        return {
            "hcp_master": self.hcp_master,
            "product": self.product,
            "call_activity": self.call_activity,
            "prescriptions": self.prescriptions,
        }


class CommercialSimulation:
    def __init__(
        self,
        hcps: int = 1000,
        years: int = 3,
        scenario: str = "new_product_launch",
        seed: int = 42,
    ):
        self.hcps = hcps
        self.years = years
        self.scenario = scenario
        self.seed = seed

        if self.scenario != "new_product_launch":
            raise ValueError("Only new_product_launch is supported in v0.1")

    def run(self) -> CommercialSimulationResult:
        hcp_master = generate_hcps(
            num_hcps=self.hcps,
            seed=self.seed,
        )

        product = generate_products(
            seed=self.seed,
            config=DEFAULT_COMMERCIAL_CONFIG,
        )

        call_activity = generate_call_activity(
            hcp_master=hcp_master,
            product=product,
            years=self.years,
            seed=self.seed,
        )

        prescriptions = generate_prescriptions(
            hcp_master=hcp_master,
            product=product,
            call_activity=call_activity,
            years=self.years,
            seed=self.seed,
        )

        return CommercialSimulationResult(
            hcp_master=hcp_master,
            product=product,
            call_activity=call_activity,
            prescriptions=prescriptions,
        )


def write_csv_outputs(
    result: CommercialSimulationResult,
    output_dir: str = "output",
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for table_name, dataframe in result.as_dict().items():
        dataframe.to_csv(output_path / f"{table_name}.csv", index=False)


def write_duckdb_output(
    result: CommercialSimulationResult,
    output_dir: str = "output",
) -> Path:
    return write_duckdb(
        datasets=result.as_dict(),
        output_dir=output_dir,
    )
