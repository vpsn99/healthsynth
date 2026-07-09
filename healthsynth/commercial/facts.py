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
        years: int = 3,
    ) -> pd.DataFrame:
        start_date = pd.Timestamp("2023-01-01")
        products = product.to_dict("records")
        market_id = self.config["market"]["market_id"]
        market_share_lookup = self._build_market_share_lookup(market_share)

        months = pd.date_range(
            start=start_date,
            periods=years * 12,
            freq="MS",
        )

        calls_by_hcp_month = self._summarize_calls(call_activity)

        rows = []
        rx_id = 1

        for _, hcp in hcp_master.iterrows():
            hcp_id = hcp["hcp_id"]
            decile = int(hcp["decile"])
            segment = hcp["segment"]

            base_nrx = self._base_nrx_from_decile(decile)
            response_multiplier = self._response_multiplier(segment)

            for month_index, rx_date in enumerate(months):
                for product_row in products:
                    product_id = product_row["product_id"]

                    month_key = rx_date.strftime("%Y-%m")
                    adjusted_market_share = market_share_lookup.get(
                        (month_key, product_id),
                        float(product_row.get("baseline_market_share", 1.0)),
                    )

                    launch_effect = self._launch_adoption_effect(month_index)

                    previous_month = rx_date - pd.DateOffset(months=1)
                    previous_month_key = previous_month.strftime("%Y-%m")
                    lagged_calls = calls_by_hcp_month.get((hcp_id, previous_month_key), 0)

                    affinity = self._product_affinity(
                        specialty=hcp["specialty"],
                        product_id=product_id,
                    )

                    call_effect = self._call_response_effect(
                        lagged_calls=lagged_calls,
                        response_multiplier=response_multiplier,
                    )

                    noise = self.rng.normal(loc=0, scale=1.5)
                    seasonality = self._seasonality_factor(rx_date.month)

                    nrx = (
                        (base_nrx * launch_effect * affinity * adjusted_market_share)
                        + (call_effect * affinity * adjusted_market_share)
                        + noise
                    ) * seasonality

                    nrx = max(0, int(round(nrx)))

                    trx_multiplier = self.rng.uniform(2.0, 3.5)
                    trx = max(nrx, int(round(nrx * trx_multiplier)))

                    rows.append(
                        {
                            "market_id": market_id,
                            "rx_id": f"RX{rx_id:09d}",
                            "rx_date": rx_date.date().isoformat(),
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
