from healthsynth.exceptions import HealthSynthConfigurationError


def validate_config(config: dict) -> None:
    """
    Validate minimum required configuration.

    This intentionally validates only rules that can break generation
    or produce misleading datasets.
    """
    _validate_generation(config)
    _validate_distribution(config, "specialty_distribution")
    _validate_distribution(config, "decile_distribution")
    _validate_distribution(config, "channel_distribution")
    _validate_products(config)
    _validate_affinity(config)


def _validate_generation(config: dict) -> None:
    generation = config.get("generation", {})

    hcps = generation.get("hcps")
    years = generation.get("years")
    seed = generation.get("seed")

    if hcps is not None and hcps <= 0:
        raise HealthSynthConfigurationError("generation.hcps must be greater than 0.")

    if years is not None and years <= 0:
        raise HealthSynthConfigurationError("generation.years must be greater than 0.")

    if seed is not None and seed < 0:
        raise HealthSynthConfigurationError("generation.seed must be greater than or equal to 0.")


def _validate_distribution(config: dict, key: str) -> None:
    distribution = config.get(key)

    if distribution is None:
        raise HealthSynthConfigurationError(f"{key} is required.")

    if not isinstance(distribution, dict) or not distribution:
        raise HealthSynthConfigurationError(f"{key} must be a non-empty mapping.")

    total = 0.0

    for item, value in distribution.items():
        if value < 0:
            raise HealthSynthConfigurationError(f"{key}.{item} must be greater than or equal to 0.")
        total += float(value)

    if abs(total - 1.0) > 0.01:
        raise HealthSynthConfigurationError(
            f"{key} must sum to approximately 1.0. Current sum: {total:.4f}"
        )


def _validate_products(config: dict) -> None:
    products = config.get("products")

    if not products:
        raise HealthSynthConfigurationError("products must contain at least one product.")

    seen_product_ids = set()

    for index, product in enumerate(products):
        product_id = product.get("product_id")
        product_name = product.get("product_name")

        if not product_id:
            raise HealthSynthConfigurationError(f"products[{index}].product_id is required.")

        if not product_name:
            raise HealthSynthConfigurationError(f"products[{index}].product_name is required.")

        if product_id in seen_product_ids:
            raise HealthSynthConfigurationError(f"Duplicate product_id found: {product_id}")

        seen_product_ids.add(product_id)


def _validate_affinity(config: dict) -> None:
    affinity = config.get("specialty_product_affinity")

    if not affinity:
        raise HealthSynthConfigurationError("specialty_product_affinity must be provided.")

    product_ids = {product["product_id"] for product in config["products"]}

    for specialty, product_affinity in affinity.items():
        if not isinstance(product_affinity, dict):
            raise HealthSynthConfigurationError(
                f"specialty_product_affinity.{specialty} must be a mapping."
            )

        for product_id, value in product_affinity.items():
            if product_id not in product_ids:
                raise HealthSynthConfigurationError(
                    f"specialty_product_affinity.{specialty}.{product_id} "
                    "references an unknown product."
                )

            if value < 0:
                raise HealthSynthConfigurationError(
                    f"specialty_product_affinity.{specialty}.{product_id} "
                    "must be greater than or equal to 0."
                )
