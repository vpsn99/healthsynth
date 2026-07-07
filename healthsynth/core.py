from copy import deepcopy

import numpy as np
from faker import Faker


class BaseGenerator:
    def __init__(
        self,
        seed: int = 42,
        locale: str = "en_CA",
        config: dict | None = None,
    ):
        self.seed = seed
        self.locale = locale
        self.config = deepcopy(config) if config else {}

        self.rng = np.random.default_rng(seed)
        self.fake = Faker(locale)
        Faker.seed(seed)
