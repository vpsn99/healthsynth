from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from healthsynth.commercial.dynamics import (
    generate_market_demand,
    generate_market_share,
    generate_promotion_effect,
)
from healthsynth.commercial.entities import generate_hcps, generate_market, generate_products
from healthsynth.commercial.facts import generate_call_activity, generate_prescriptions
from healthsynth.config.loader import ConfigLoader
from healthsynth.exporters.duckdb_exporter import write_duckdb


@dataclass
class CommercialSimulationResult:
    hcp_master: pd.DataFrame
    product: pd.DataFrame
    call_activity: pd.DataFrame
    prescriptions: pd.DataFrame
    market: pd.DataFrame
    promotion_effect: pd.DataFrame
    market_share: pd.DataFrame
    market_demand: pd.DataFrame

    def as_dict(self) -> dict[str, pd.DataFrame]:
        return {
            "market": self.market,
            "hcp_master": self.hcp_master,
            "product": self.product,
            "promotion_effect": self.promotion_effect,
            "market_share": self.market_share,
            "call_activity": self.call_activity,
            "prescriptions": self.prescriptions,
            "market_demand": self.market_demand,
        }


class CommercialSimulation:
    def __init__(
        self,
        hcps: int = 1000,
        years: int = 3,
        scenario: str = "new_product_launch",
        seed: int = 42,
        config_path: str | None = None,
    ):
        self.hcps = hcps
        self.years = years
        self.scenario = scenario
        self.seed = seed
        self.config_path = config_path

        if self.scenario != "new_product_launch":
            raise ValueError("Only new_product_launch is supported in v0.1")

    def run(self) -> CommercialSimulationResult:
        config = ConfigLoader.load(self.config_path)

        market = generate_market(
            seed=self.seed,
            config=config,
        )

        hcp_master = generate_hcps(
            num_hcps=self.hcps,
            seed=self.seed,
            config=config,
        )

        product = generate_products(
            seed=self.seed,
            config=config,
        )

        market_demand = generate_market_demand(
            product=product,
            years=self.years,
            seed=self.seed,
            config=config,
        )

        call_activity = generate_call_activity(
            hcp_master=hcp_master,
            product=product,
            years=self.years,
            seed=self.seed,
            config=config,
        )

        promotion_effect = generate_promotion_effect(
            call_activity=call_activity,
            seed=self.seed,
            config=config,
        )

        market_share = generate_market_share(
            product=product,
            promotion_effect=promotion_effect,
            years=self.years,
            seed=self.seed,
            config=config,
        )

        prescriptions = generate_prescriptions(
            hcp_master=hcp_master,
            product=product,
            call_activity=call_activity,
            market_share=market_share,
            years=self.years,
            seed=self.seed,
            config=config,
        )

        return CommercialSimulationResult(
            market=market,
            hcp_master=hcp_master,
            product=product,
            market_demand=market_demand,
            call_activity=call_activity,
            promotion_effect=promotion_effect,
            market_share=market_share,
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
