from healthsynth.exceptions import HealthSynthConfigurationError

VALID_BRAND_TYPES = {
    "Innovator",
    "Competitor",
}


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

        manufacturer = product.get("manufacturer")
        brand_type = product.get("brand_type")
        baseline_market_share = product.get("baseline_market_share")

        if not manufacturer:
            raise HealthSynthConfigurationError(f"products[{index}].manufacturer is required.")

        if not brand_type:
            raise HealthSynthConfigurationError(f"products[{index}].brand_type is required.")

        if baseline_market_share is None:
            raise HealthSynthConfigurationError(
                f"products[{index}].baseline_market_share is required."
            )

        if brand_type not in VALID_BRAND_TYPES:
            raise HealthSynthConfigurationError(
                f"products[{index}].brand_type must be one of: "
                f"{', '.join(sorted(VALID_BRAND_TYPES))}"
            )

        if baseline_market_share < 0:
            raise HealthSynthConfigurationError(
                f"products[{index}].baseline_market_share must be greater than or equal to 0."
            )

        if product_id in seen_product_ids:
            raise HealthSynthConfigurationError(f"Duplicate product_id found: {product_id}")

    _validate_baseline_market_share(products)

    seen_product_ids.add(product_id)


def _validate_baseline_market_share(products: list[dict]) -> None:
    shares_by_area = {}

    for product in products:
        therapeutic_area = product.get("therapeutic_area", "Unknown")
        shares_by_area[therapeutic_area] = shares_by_area.get(therapeutic_area, 0.0) + float(
            product.get("baseline_market_share", 0.0)
        )

    for therapeutic_area, total_share in shares_by_area.items():
        if abs(total_share - 1.0) > 0.01:
            raise HealthSynthConfigurationError(
                "baseline_market_share must sum to approximately 1.0 "
                f"within therapeutic_area '{therapeutic_area}'. "
                f"Current sum: {total_share:.4f}"
            )


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
