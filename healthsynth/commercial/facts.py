import numpy as np
import pandas as pd


class CallActivityGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
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

    def generate(
        self,
        hcp_master: pd.DataFrame,
        product: pd.DataFrame,
        years: int = 3,
    ) -> pd.DataFrame:
        start_date = pd.Timestamp("2023-01-01")
        end_date = start_date + pd.DateOffset(years=years)

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
                            "call_id": f"CALL{call_id:09d}",
                            "call_date": call_date.date().isoformat(),
                            "hcp_id": hcp["hcp_id"],
                            "rep_id": hcp["rep_id"],
                            "product_id": product_id,
                            "channel": "Rep Call",
                            "sample_dropped": bool(self.rng.random() < 0.25),
                        }
                    )
                    call_id += 1

        return pd.DataFrame(call_rows)


class PrescriptionGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed + 1000)

    def generate(
        self,
        hcp_master: pd.DataFrame,
        product: pd.DataFrame,
        call_activity: pd.DataFrame,
        years: int = 3,
    ) -> pd.DataFrame:
        start_date = pd.Timestamp("2023-01-01")
        product_id = product.iloc[0]["product_id"]

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
                launch_effect = self._launch_adoption_effect(month_index)

                previous_month = rx_date - pd.DateOffset(months=1)
                previous_month_key = previous_month.strftime("%Y-%m")
                lagged_calls = calls_by_hcp_month.get((hcp_id, previous_month_key), 0)

                call_effect = lagged_calls * response_multiplier * 0.8

                noise = self.rng.normal(loc=0, scale=1.5)

                nrx = base_nrx * launch_effect + call_effect + noise
                nrx = max(0, int(round(nrx)))

                trx_multiplier = self.rng.uniform(2.0, 3.5)
                trx = max(nrx, int(round(nrx * trx_multiplier)))

                rows.append(
                    {
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

    def _summarize_calls(self, call_activity: pd.DataFrame) -> dict:
        if call_activity.empty:
            return {}

        calls = call_activity.copy()
        calls["call_month"] = pd.to_datetime(calls["call_date"]).dt.strftime("%Y-%m")

        grouped = calls.groupby(["hcp_id", "call_month"]).size().reset_index(name="call_count")

        return {
            (row["hcp_id"], row["call_month"]): int(row["call_count"])
            for _, row in grouped.iterrows()
        }

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
    years: int = 3,
    seed: int = 42,
) -> pd.DataFrame:
    return PrescriptionGenerator(seed=seed).generate(
        hcp_master=hcp_master,
        product=product,
        call_activity=call_activity,
        years=years,
    )


def generate_call_activity(
    hcp_master: pd.DataFrame,
    product: pd.DataFrame,
    years: int = 3,
    seed: int = 42,
) -> pd.DataFrame:
    return CallActivityGenerator(seed=seed).generate(
        hcp_master=hcp_master,
        product=product,
        years=years,
    )
