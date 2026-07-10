import numpy as np
import pandas as pd

from healthsynth.config.loader import ConfigLoader


class CommercialDemandGenerator:
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
        self.rng = np.random.default_rng(seed + 3000)

    def generate(
        self,
        product: pd.DataFrame,
        years: int = 3,
    ) -> pd.DataFrame:
        market_id = self.config["market"]["market_id"]
        demand_config = self.config["market_demand"]

        start_date = pd.Timestamp("2023-01-01")
        end_date = start_date + pd.DateOffset(years=years)
        months = pd.date_range(
            start=start_date,
            end=end_date,
            freq="MS",
            inclusive="left",
        )

        therapeutic_areas = sorted(product["therapeutic_area"].unique())
        rows = []

        for area in therapeutic_areas:
            base_market_nrx = float(demand_config["base_monthly_nrx"].get(area, 500))

            for month_index, month_start in enumerate(months):
                growth_factor = (1 + float(demand_config["monthly_growth_rate"])) ** month_index

                seasonality_factor = float(demand_config["seasonality"].get(month_start.month, 1.0))

                noise = self.rng.normal(loc=1.0, scale=0.03)

                market_nrx = max(
                    0,
                    int(round(base_market_nrx * growth_factor * seasonality_factor * noise)),
                )

                rows.append(
                    {
                        "market_id": market_id,
                        "month": month_start.date().isoformat(),
                        "therapeutic_area": area,
                        "base_market_nrx": base_market_nrx,
                        "growth_factor": growth_factor,
                        "seasonality_factor": seasonality_factor,
                        "market_nrx": market_nrx,
                    }
                )

        return pd.DataFrame(rows)


class PromotionEffectGenerator:
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

    def generate(
        self,
        call_activity: pd.DataFrame,
    ) -> pd.DataFrame:
        weights = self.config["channel_response_multiplier"]

        activity = call_activity.copy()
        activity["month"] = pd.to_datetime(activity["call_date"]).dt.to_period("M").astype(str)
        activity["channel_weight"] = activity["channel"].map(weights).fillna(1.0)

        promotion = (
            activity.groupby(["market_id", "month", "product_id"])["channel_weight"]
            .sum()
            .reset_index(name="promotion_score")
        )

        max_score = promotion["promotion_score"].max()

        if max_score > 0:
            promotion["promotion_index"] = promotion["promotion_score"] / max_score
        else:
            promotion["promotion_index"] = 0.0

        return promotion


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
        promotion_effect: pd.DataFrame | None = None,
        years: int = 3,
    ) -> pd.DataFrame:
        market_id = self.config["market"]["market_id"]

        promotion_lookup = self._build_promotion_lookup(promotion_effect)
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
                    month_key = month_start.strftime("%Y-%m")
                    promotion_index = promotion_lookup.get(
                        (month_key, product_row["product_id"]), 0.0
                    )
                    promotion_effect_value = 0.10 * promotion_index

                    launch_effect = self._launch_effect(month_index)
                    noise = self.rng.normal(loc=0.0, scale=0.01)

                    adjusted_score = max(
                        0.001,
                        baseline_share * launch_effect + promotion_effect_value + noise,
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

    @staticmethod
    def _build_promotion_lookup(
        promotion_effect: pd.DataFrame | None,
    ) -> dict:
        if promotion_effect is None or promotion_effect.empty:
            return {}

        return {
            (row["month"], row["product_id"]): float(row["promotion_index"])
            for _, row in promotion_effect.iterrows()
        }


def generate_market_share(
    product: pd.DataFrame,
    promotion_effect: pd.DataFrame | None = None,
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
        promotion_effect=promotion_effect,
        years=years,
    )


def generate_promotion_effect(
    call_activity: pd.DataFrame,
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return PromotionEffectGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate(call_activity=call_activity)


def generate_market_demand(
    product: pd.DataFrame,
    years: int = 3,
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return CommercialDemandGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate(
        product=product,
        years=years,
    )
