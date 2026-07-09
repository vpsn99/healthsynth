import numpy as np
import pandas as pd

from healthsynth.config.loader import ConfigLoader


class MarketShareGenerator:
    def __init__(
        self,
        seed: int = 42,
        config: dict | None = None,
        config_path: str | None = None,
    ):
        if config is None:
            config = ConfigLoader.load(config_path)

        self.seed = seed
        self.config = config
        self.rng = np.random.default_rng(seed + 2000)

    def generate(
        self,
        product: pd.DataFrame,
        years: int = 3,
    ) -> pd.DataFrame:
        market_id = self.config["market"]["market_id"]

        start_date = pd.Timestamp("2023-01-01")
        end_date = start_date + pd.DateOffset(years=years)
        months = pd.date_range(
            start=start_date,
            end=end_date,
            freq="MS",
            inclusive="left",
        )

        rows = []

        for therapeutic_area, area_products in product.groupby("therapeutic_area"):
            for month_index, month_start in enumerate(months):
                raw_scores = []

                for _, product_row in area_products.iterrows():
                    baseline_share = float(product_row["baseline_market_share"])

                    launch_effect = self._launch_effect(month_index)
                    noise = self.rng.normal(loc=0.0, scale=0.01)

                    adjusted_score = max(
                        0.001,
                        baseline_share * launch_effect + noise,
                    )

                    raw_scores.append(
                        {
                            "market_id": market_id,
                            "month": month_start.date().isoformat(),
                            "therapeutic_area": therapeutic_area,
                            "product_id": product_row["product_id"],
                            "baseline_market_share": baseline_share,
                            "raw_score": adjusted_score,
                        }
                    )

                total_score = sum(row["raw_score"] for row in raw_scores)

                for row in raw_scores:
                    adjusted_market_share = row["raw_score"] / total_score

                    rows.append(
                        {
                            "market_id": row["market_id"],
                            "month": row["month"],
                            "therapeutic_area": row["therapeutic_area"],
                            "product_id": row["product_id"],
                            "baseline_market_share": row["baseline_market_share"],
                            "adjusted_market_share": adjusted_market_share,
                        }
                    )

        return pd.DataFrame(rows)

    @staticmethod
    def _launch_effect(month_index: int) -> float:
        """
        Simple early market evolution factor.

        This is intentionally modest for v1 because baseline market share
        remains the main driver. Future versions can make this scenario-driven.
        """
        return min(1.15, 0.90 + month_index * 0.01)


def generate_market_share(
    product: pd.DataFrame,
    years: int = 3,
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return MarketShareGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate(
        product=product,
        years=years,
    )
