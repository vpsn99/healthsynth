from dataclasses import dataclass

import pandas as pd

from healthsynth.config.defaults import DEFAULT_CONFIG
from healthsynth.core import BaseGenerator


@dataclass
class Territory:
    territory_id: str
    territory_name: str
    rep_id: str
    rep_name: str


class HCPGenerator(BaseGenerator):
    def __init__(self, seed: int = 42, config: dict | None = None):
        merged_config = DEFAULT_CONFIG.copy()
        if config:
            merged_config.update(config)

        super().__init__(
            seed=seed,
            config=merged_config,
        )

        self.territories = self._generate_territories()

    def generate(self, num_hcps: int = 1000) -> pd.DataFrame:
        rows = []

        specialties = list(self.config["specialty_distribution"].keys())
        specialty_probs = list(self.config["specialty_distribution"].values())

        deciles = list(self.config["decile_distribution"].keys())
        decile_probs = list(self.config["decile_distribution"].values())

        for i in range(1, num_hcps + 1):
            hcp_id = f"HCP{i:06d}"
            decile = int(self.rng.choice(deciles, p=decile_probs))
            territory = self.rng.choice(self.territories)

            rows.append(
                {
                    "hcp_id": hcp_id,
                    "hcp_name": self.fake.name(),
                    "specialty": self.rng.choice(specialties, p=specialty_probs),
                    "decile": decile,
                    "segment": self._segment_from_decile(decile),
                    "territory_id": territory.territory_id,
                    "territory_name": territory.territory_name,
                    "rep_id": territory.rep_id,
                    "rep_name": territory.rep_name,
                    "city": self.fake.city(),
                    "province": self.fake.province(),
                }
            )

        return pd.DataFrame(rows)

    def _generate_territories(self) -> list[Territory]:
        territories = []

        for i in range(1, self.config["num_territories"] + 1):
            territories.append(
                Territory(
                    territory_id=f"T{i:03d}",
                    territory_name=f"Territory {i:03d}",
                    rep_id=f"REP{i:03d}",
                    rep_name=self.fake.name(),
                )
            )

        return territories

    @staticmethod
    def _segment_from_decile(decile: int) -> str:
        if decile <= 3:
            return "Low"
        if decile <= 7:
            return "Medium"
        return "High"


class ProductGenerator(BaseGenerator):
    def __init__(self, seed: int = 42, config: dict | None = None):
        super().__init__(
            seed=seed,
            config=config,
        )

    def generate(self) -> pd.DataFrame:
        return pd.DataFrame(self.config["products"])


def generate_hcps(num_hcps: int = 1000, seed: int = 42, config: dict | None = None) -> pd.DataFrame:
    return HCPGenerator(seed=seed, config=config).generate(num_hcps=num_hcps)


def generate_products(seed: int = 42, config: dict | None = None) -> pd.DataFrame:
    return ProductGenerator(seed=seed, config=config).generate()
