import numpy as np
import pandas as pd

from healthsynth.config.loader import ConfigLoader
from healthsynth.simulation.calendar import build_simulation_months


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

        start_date = self.config.get("generation", {}).get(
            "start_date",
            "2023-01-01",
        )

        months = build_simulation_months(
            start_date=start_date,
            years=years,
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
        start_date = self.config.get("generation", {}).get(
            "start_date",
            "2023-01-01",
        )

        months = build_simulation_months(
            start_date=start_date,
            years=years,
        )

        rows = []

        for therapeutic_area, area_products in product.groupby("therapeutic_area"):
            for month_start in months:
                raw_scores = []

                for _, product_row in area_products.iterrows():
                    baseline_share = float(product_row["baseline_market_share"])

                    base_adoption_factor = self._adoption_factor(
                        product_row=product_row,
                        month_start=month_start,
                    )

                    month_key = month_start.strftime("%Y-%m")
                    promotion_index = promotion_lookup.get(
                        (month_key, product_row["product_id"]),
                        0.0,
                    )

                    promotion_acceleration = self._promotion_acceleration(
                        base_adoption_factor=base_adoption_factor,
                        promotion_index=promotion_index,
                        product_row=product_row,
                    )

                    effective_adoption_factor = min(
                        1.0,
                        base_adoption_factor + promotion_acceleration,
                    )

                    if effective_adoption_factor == 0.0:
                        adjusted_score = 0.0
                    else:
                        promotion_effect_value = 0.10 * promotion_index
                        noise = self.rng.normal(loc=0.0, scale=0.01)

                        mature_score = max(
                            0.001,
                            baseline_share + promotion_effect_value + noise,
                        )

                        adjusted_score = mature_score * effective_adoption_factor

                    raw_scores.append(
                        {
                            "market_id": market_id,
                            "month": month_start.date().isoformat(),
                            "therapeutic_area": therapeutic_area,
                            "product_id": product_row["product_id"],
                            "baseline_market_share": baseline_share,
                            "base_adoption_factor": base_adoption_factor,
                            "promotion_acceleration": promotion_acceleration,
                            "effective_adoption_factor": effective_adoption_factor,
                            "raw_score": adjusted_score,
                        }
                    )

                total_score = sum(row["raw_score"] for row in raw_scores)

                if total_score <= 0:
                    raise ValueError(
                        f"No active products found for therapeutic area "
                        f"'{therapeutic_area}' in {month_start:%Y-%m}."
                    )

                for row in raw_scores:
                    adjusted_market_share = row["raw_score"] / total_score

                    rows.append(
                        {
                            "market_id": row["market_id"],
                            "month": row["month"],
                            "therapeutic_area": row["therapeutic_area"],
                            "product_id": row["product_id"],
                            "baseline_market_share": row["baseline_market_share"],
                            "base_adoption_factor": row["base_adoption_factor"],
                            "promotion_acceleration": row["promotion_acceleration"],
                            "effective_adoption_factor": row["effective_adoption_factor"],
                            "adjusted_market_share": adjusted_market_share,
                        }
                    )

        return pd.DataFrame(rows)

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

    @staticmethod
    def _adoption_factor(
        product_row: pd.Series,
        month_start: pd.Timestamp,
    ) -> float:
        launch_date = pd.Timestamp(product_row["launch_date"]).to_period("M")
        simulation_month = month_start.to_period("M")

        months_since_launch = (
            (simulation_month.year - launch_date.year) * 12
            + simulation_month.month
            - launch_date.month
        )

        if months_since_launch < 0:
            return 0.0

        adoption_months_value = product_row.get("adoption_months")
        launch_factor_value = product_row.get("launch_share_factor")

        # Products without adoption configuration are treated as fully adopted
        # from their launch month onward. This preserves existing behaviour.
        if pd.isna(adoption_months_value):
            return 1.0

        adoption_months = int(adoption_months_value)

        if adoption_months <= 0:
            return 1.0

        launch_share_factor = 0.10 if pd.isna(launch_factor_value) else float(launch_factor_value)

        progress = min(months_since_launch / adoption_months, 1.0)

        return launch_share_factor + (1.0 - launch_share_factor) * progress

    @staticmethod
    def _promotion_acceleration(
        base_adoption_factor: float,
        promotion_index: float,
        product_row: pd.Series,
    ) -> float:
        # Promotion cannot accelerate a product that is not yet available.
        if base_adoption_factor <= 0.0:
            return 0.0

        weight_value = product_row.get("promotion_adoption_weight")

        if pd.isna(weight_value):
            return 0.0

        promotion_adoption_weight = float(weight_value)

        remaining_gap = max(
            0.0,
            1.0 - base_adoption_factor,
        )

        return promotion_index * promotion_adoption_weight * remaining_gap

    @staticmethod
    def _redistribute_launch_share(
        shares: dict[str, float],
        area_products: pd.DataFrame,
        month_start: pd.Timestamp,
    ) -> dict[str, float]:
        redistributed = shares.copy()

        for _, launch_product in area_products.iterrows():
            source_weights = launch_product.get("share_source_weights")

            if not isinstance(source_weights, dict):
                continue

            product_id = launch_product["product_id"]
            launch_share = redistributed.get(product_id, 0.0)

            if launch_share <= 0.0:
                continue

            # First remove the launch product’s share from the
            # proportional-normalization result so it can be reassigned
            # explicitly.
            incumbent_total = sum(redistributed.get(source_id, 0.0) for source_id in source_weights)

            if incumbent_total <= 0.0:
                continue

            for source_id, source_weight in source_weights.items():
                share_loss = launch_share * float(source_weight)

                redistributed[source_id] = max(
                    0.0,
                    redistributed.get(source_id, 0.0) - share_loss,
                )

        total = sum(redistributed.values())

        if total <= 0:
            raise ValueError("Market share redistribution produced zero total share.")

        return {product_id: share / total for product_id, share in redistributed.items()}


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
