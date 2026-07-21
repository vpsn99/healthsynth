from dataclasses import dataclass

import pandas as pd

from healthsynth.config.loader import ConfigLoader
from healthsynth.core import BaseGenerator


@dataclass
class Territory:
    territory_id: str
    territory_name: str
    rep_id: str
    rep_name: str


class HCPGenerator(BaseGenerator):
    def __init__(
        self,
        seed: int = 42,
        config: dict | None = None,
        config_path: str | None = None,
    ):
        if config is None:
            config = ConfigLoader.load(config_path)

        super().__init__(
            seed=seed,
            config=config,
        )

        self.territories = self._generate_territories()

    def generate(self, num_hcps: int = 1000) -> pd.DataFrame:
        rows = []

        market_id = self.config["market"]["market_id"]

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
                    "market_id": market_id,
                    "hcp_id": hcp_id,
                    "hcp_name": self.localized_value(
                        "name",
                        fallback=f"Synthetic HCP {i:06d}",
                    ),
                    "specialty": self.rng.choice(specialties, p=specialty_probs),
                    "decile": decile,
                    "segment": self._segment_from_decile(decile),
                    "territory_id": territory.territory_id,
                    "territory_name": territory.territory_name,
                    "rep_id": territory.rep_id,
                    "rep_name": territory.rep_name,
                    "address": self.localized_value(
                        "street_address",
                    ),
                    "city": self.localized_value(
                        "city",
                    ),
                    "administrative_area": self.localized_value(
                        "administrative_unit",
                        "state",
                        "province",
                    ),
                    "postal_code": self.localized_value(
                        "postcode",
                        "postalcode",
                    ),
                    "phone_number": self.localized_value(
                        "phone_number",
                    ),
                    "country_code": self.country_code,
                    "country_name": self.country_name,
                    "faker_locale": self.locale,
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
                    rep_name=self.localized_value(
                        "name",
                        fallback=f"Synthetic Rep {i:03d}",
                    ),
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
    def __init__(
        self,
        seed: int = 42,
        config: dict | None = None,
        config_path: str | None = None,
    ):
        if config is None:
            config = ConfigLoader.load(config_path)

        super().__init__(
            seed=seed,
            config=config,
        )

    def generate(self) -> pd.DataFrame:
        market_id = self.config["market"]["market_id"]

        products = []

        for product in self.config["products"]:
            row = {
                "market_id": market_id,
                **product,
            }
            products.append(row)

        return pd.DataFrame(products)


class MarketGenerator(BaseGenerator):
    def __init__(
        self,
        seed: int = 42,
        config: dict | None = None,
        config_path: str | None = None,
    ):
        if config is None:
            config = ConfigLoader.load(config_path)

        super().__init__(
            seed=seed,
            config=config,
        )

    def generate(self) -> pd.DataFrame:
        market = self.config["market"]

        return pd.DataFrame(
            [
                {
                    "market_id": market["market_id"],
                    "market_name": market["market_name"],
                    "country": market["country"],
                    "locale": self.config.get("locale"),
                    "profile_name": self.config.get("profile_name", "custom"),
                }
            ]
        )


def generate_hcps(
    num_hcps: int = 1000,
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return HCPGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate(num_hcps=num_hcps)


def generate_products(
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return ProductGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate()


def generate_market(
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return MarketGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate()
