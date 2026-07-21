from copy import deepcopy

import numpy as np
from faker import Faker


class BaseGenerator:
    def __init__(
        self,
        seed: int = 42,
        locale: str | None = None,
        config: dict | None = None,
    ):
        self.seed = seed
        self.config = deepcopy(config) if config else {}

        locality = self.config.get(
            "locality",
            {},
        )

        self.locale = locale or locality.get("faker_locale") or "en_CA"

        self.country_code = locality.get(
            "country_code",
            "CA",
        )
        self.country_name = locality.get(
            "country_name",
            "Canada",
        )
        self.currency_code = locality.get(
            "currency_code",
            "CAD",
        )
        self.timezone = locality.get(
            "timezone",
            "America/Toronto",
        )

        self.rng = np.random.default_rng(seed)

        self.fake = Faker(self.locale)
        self.fake.seed_instance(seed)

    def localized_value(
        self,
        *provider_names: str,
        fallback: str = "",
    ) -> str:
        """Return the first available localized Faker value."""

        for provider_name in provider_names:
            provider = getattr(
                self.fake,
                provider_name,
                None,
            )

            if provider is None:
                continue

            try:
                value = provider()
            except (
                AttributeError,
                NotImplementedError,
            ):
                continue

            if value is not None:
                return str(value)

        return fallback
