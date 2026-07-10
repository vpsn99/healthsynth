import numpy as np
import pandas as pd

from healthsynth.config.loader import ConfigLoader


class CallActivityGenerator:
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
        self.rng = np.random.default_rng(seed)

    def _monthly_call_rate(
        self,
        decile: int,
        segment: str,
        month_index: int,
    ) -> float:
        """
        Estimate monthly rep call intensity.

        Business logic:
        - Higher decile HCPs receive more calls.
        - High segment HCPs are prioritized.
        - Summer and December have slightly lower activity.
        """

        if segment == "High":
            base_rate = 3.0
        elif segment == "Medium":
            base_rate = 1.5
        else:
            base_rate = 0.5

        decile_lift = decile / 10

        seasonal_factor = 1.0
        if month_index in [7, 8, 12]:
            seasonal_factor = 0.75

        return base_rate * (0.75 + decile_lift) * seasonal_factor

    def _choose_channel(self) -> str:
        distribution = self.config["channel_distribution"]

        channels = list(distribution.keys())
        weights = list(distribution.values())

        return self.rng.choice(
            channels,
            p=weights,
        )

    def generate(
        self,
        hcp_master: pd.DataFrame,
        product: pd.DataFrame,
        years: int = 3,
    ) -> pd.DataFrame:
        start_date = pd.Timestamp("2023-01-01")
        end_date = start_date + pd.DateOffset(years=years)

        market_id = self.config["market"]["market_id"]
        product_id = product.iloc[0]["product_id"]
        call_rows = []
        call_id = 1

        for _, hcp in hcp_master.iterrows():
            segment = hcp["segment"]

            months = pd.date_range(start=start_date, end=end_date, freq="MS", inclusive="left")

            for month_start in months:
                monthly_call_rate = self._monthly_call_rate(
                    decile=int(hcp["decile"]),
                    segment=segment,
                    month_index=month_start.month,
                )

                num_calls = int(self.rng.poisson(monthly_call_rate))

                for _ in range(num_calls):
                    days_in_month = month_start.days_in_month
                    call_day = int(self.rng.integers(1, days_in_month + 1))
                    call_date = month_start.replace(day=call_day)

                    call_rows.append(
                        {
                            "market_id": market_id,
                            "call_id": f"CALL{call_id:09d}",
                            "call_date": call_date.date().isoformat(),
                            "hcp_id": hcp["hcp_id"],
                            "rep_id": hcp["rep_id"],
                            "product_id": product_id,
                            "channel": self._choose_channel(),
                            "sample_dropped": bool(self.rng.random() < 0.25),
                        }
                    )
                    call_id += 1

        return pd.DataFrame(call_rows)


class PrescriptionGenerator:
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
        self.rng = np.random.default_rng(seed + 1000)

    def generate(
        self,
        hcp_master: pd.DataFrame,
        product: pd.DataFrame,
        call_activity: pd.DataFrame,
        market_share: pd.DataFrame,
        market_demand: pd.DataFrame,
        years: int = 3,
    ) -> pd.DataFrame:
        market_id = self.config["market"]["market_id"]

        demand_lookup = self._build_market_demand_lookup(market_demand)
        share_lookup = self._build_market_share_lookup(market_share)

        call_summary = self._summarize_calls(call_activity)

        start_date = pd.Timestamp("2023-01-01")
        end_date = start_date + pd.DateOffset(years=years)

        months = pd.date_range(
            start=start_date,
            end=end_date,
            freq="MS",
            inclusive="left",
        )

        rows = []
        rx_id = 1

        hcp_ids = hcp_master["hcp_id"].to_numpy()
        hcp_specialties = hcp_master["specialty"].to_numpy()
        hcp_deciles = hcp_master["decile"].astype(float).to_numpy()

        decile_weights = 0.25 + hcp_deciles / 10.0

        affinity_by_product = {
            product_id: np.array(
                [
                    self._product_affinity(
                        specialty=specialty,
                        product_id=product_id,
                    )
                    for specialty in hcp_specialties
                ],
                dtype=float,
            )
            for product_id in product["product_id"]
        }

        for therapeutic_area, area_products in product.groupby("therapeutic_area"):
            area_products = area_products.reset_index(drop=True)

            for month_start in months:
                month_key = month_start.strftime("%Y-%m")

                market_nrx = demand_lookup.get(
                    (month_key, therapeutic_area),
                    0,
                )

                product_shares = np.array(
                    [
                        share_lookup.get(
                            (
                                month_key,
                                therapeutic_area,
                                product_row["product_id"],
                            ),
                            float(product_row["baseline_market_share"]),
                        )
                        for _, product_row in area_products.iterrows()
                    ],
                    dtype=float,
                )

                product_nrx_allocations = self._allocate_counts(
                    total=market_nrx,
                    weights=product_shares,
                )

                for product_index, product_row in area_products.iterrows():
                    product_id = product_row["product_id"]
                    product_nrx = int(product_nrx_allocations[product_index])

                    affinity_weights = affinity_by_product[product_id]

                    weighted_calls = np.array(
                        [
                            call_summary.get(
                                (month_key, hcp_id, product_id),
                                0.0,
                            )
                            for hcp_id in hcp_ids
                        ],
                        dtype=float,
                    )

                    engagement_weights = 1.0 + 0.15 * np.log1p(weighted_calls)

                    hcp_weights = np.maximum(
                        0.001,
                        affinity_weights * decile_weights * engagement_weights,
                    )

                    hcp_nrx_allocations = self._allocate_counts(
                        total=product_nrx,
                        weights=np.array(hcp_weights),
                    )

                    for hcp_position, hcp_id in enumerate(hcp_ids):
                        nrx = int(hcp_nrx_allocations[hcp_position])

                        trx_multiplier = max(
                            1.0,
                            self.rng.normal(loc=2.2, scale=0.25),
                        )
                        trx = max(nrx, int(round(nrx * trx_multiplier)))

                        rows.append(
                            {
                                "market_id": market_id,
                                "rx_id": f"RX{rx_id:09d}",
                                "rx_date": month_start.date().isoformat(),
                                "hcp_id": hcp_id,
                                "product_id": product_id,
                                "nrx": nrx,
                                "trx": trx,
                            }
                        )

                        rx_id += 1

        return pd.DataFrame(rows)

    def _summarize_calls(
        self,
        call_activity: pd.DataFrame,
    ) -> dict:
        weights = self.config["channel_response_multiplier"]

        summary = {}

        for _, row in call_activity.iterrows():
            key = (
                row["hcp_id"],
                pd.to_datetime(row["call_date"]).strftime("%Y-%m"),
            )

            weight = weights.get(
                row["channel"],
                1.0,
            )

            summary[key] = summary.get(key, 0) + weight

        return summary

    @staticmethod
    def _build_market_share_lookup(
        market_share: pd.DataFrame,
    ) -> dict:
        lookup = {}

        for _, row in market_share.iterrows():
            lookup[
                (
                    pd.to_datetime(row["month"]).strftime("%Y-%m"),
                    row["product_id"],
                )
            ] = float(row["adjusted_market_share"])

        return lookup

    @staticmethod
    def _build_market_demand_lookup(
        market_demand: pd.DataFrame,
    ) -> dict:
        return {
            (
                pd.to_datetime(row["month"]).strftime("%Y-%m"),
                row["therapeutic_area"],
            ): int(row["market_nrx"])
            for _, row in market_demand.iterrows()
        }

    @staticmethod
    def _build_market_share_lookup(
        market_share: pd.DataFrame,
    ) -> dict:
        return {
            (
                pd.to_datetime(row["month"]).strftime("%Y-%m"),
                row["therapeutic_area"],
                row["product_id"],
            ): float(row["adjusted_market_share"])
            for _, row in market_share.iterrows()
        }

    def _allocate_counts(
        self,
        total: int,
        weights: np.ndarray,
    ) -> np.ndarray:
        if total <= 0:
            return np.zeros(len(weights), dtype=int)

        weights = np.asarray(weights, dtype=float)
        weights = np.clip(weights, 0.0, None)

        weight_sum = weights.sum()

        if weight_sum <= 0:
            probabilities = np.full(len(weights), 1.0 / len(weights))
        else:
            probabilities = weights / weight_sum

        return self.rng.multinomial(total, probabilities)

    @staticmethod
    def _call_response_effect(
        lagged_calls: int,
        response_multiplier: float,
    ) -> float:
        """
        Estimate lagged call impact using diminishing returns.

        This uses log1p as a simple first version of a saturation curve.
        Future versions may support configurable response functions such as
        linear, square-root, or Hill curves.
        """
        return np.log1p(lagged_calls) * response_multiplier * 2.0

    def _product_affinity(
        self,
        specialty: str,
        product_id: str,
    ) -> float:
        affinity_map = self.config["specialty_product_affinity"]

        if specialty not in affinity_map:
            return 0.25

        return affinity_map[specialty].get(product_id, 0.10)

    @staticmethod
    def _seasonality_factor(month: int) -> float:
        """
        Simple seasonality adjustment.

        July, August, and December are modeled as lower-activity months.
        Future versions should move this into configuration.
        """
        if month in [7, 8, 12]:
            return 0.85

        return 1.0

    @staticmethod
    def _base_nrx_from_decile(decile: int) -> float:
        return 0.4 + (decile * 0.7)

    @staticmethod
    def _response_multiplier(segment: str) -> float:
        if segment == "High":
            return 1.5
        if segment == "Medium":
            return 1.0
        return 0.5

    @staticmethod
    def _launch_adoption_effect(month_index: int) -> float:
        """
        Simple S-curve-like launch adoption effect.

        Early months are low, middle months accelerate,
        later months plateau.
        """
        return 1 / (1 + np.exp(-0.25 * (month_index - 12)))


def generate_prescriptions(
    hcp_master: pd.DataFrame,
    product: pd.DataFrame,
    call_activity: pd.DataFrame,
    market_share: pd.DataFrame,
    market_demand: pd.DataFrame,
    years: int = 3,
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return PrescriptionGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate(
        hcp_master=hcp_master,
        product=product,
        call_activity=call_activity,
        market_share=market_share,
        market_demand=market_demand,
        years=years,
    )


def generate_call_activity(
    hcp_master: pd.DataFrame,
    product: pd.DataFrame,
    years: int = 3,
    seed: int = 42,
    config: dict | None = None,
    config_path: str | None = None,
) -> pd.DataFrame:
    return CallActivityGenerator(
        seed=seed,
        config=config,
        config_path=config_path,
    ).generate(
        hcp_master=hcp_master,
        product=product,
        years=years,
    )
