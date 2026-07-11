import pandas as pd

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
    _validate_market(config)


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

        adoption_curve = product.get("adoption_curve")
        adoption_months = product.get("adoption_months")
        launch_share_factor = product.get("launch_share_factor")
        promotion_adoption_weight = product.get("promotion_adoption_weight")

        loe_date = product.get("loe_date")
        loe_erosion_months = product.get("loe_erosion_months")
        post_loe_share_factor = product.get("post_loe_share_factor")

        share_source_weights = product.get("share_source_weights")

        if loe_date is not None:
            try:
                pd.Timestamp(loe_date)
            except (TypeError, ValueError) as exc:
                raise HealthSynthConfigurationError(
                    f"products[{index}].loe_date must be a valid date."
                ) from exc

        if loe_erosion_months is not None and loe_erosion_months <= 0:
            raise HealthSynthConfigurationError(
                f"products[{index}].loe_erosion_months must be greater than 0."
            )

        if post_loe_share_factor is not None and not 0 <= post_loe_share_factor <= 1:
            raise HealthSynthConfigurationError(
                f"products[{index}].post_loe_share_factor must be between 0 and 1."
            )

        if loe_date is not None and loe_erosion_months is None:
            raise HealthSynthConfigurationError(
                f"products[{index}].loe_erosion_months is required when loe_date is configured."
            )

        if loe_date is not None and post_loe_share_factor is None:
            raise HealthSynthConfigurationError(
                f"products[{index}].post_loe_share_factor is required when loe_date is configured."
            )

        if share_source_weights is not None:
            if not isinstance(share_source_weights, dict):
                raise HealthSynthConfigurationError(
                    f"products[{index}].share_source_weights must be a mapping."
                )

            if not share_source_weights:
                raise HealthSynthConfigurationError(
                    f"products[{index}].share_source_weights cannot be empty."
                )

            total_weight = 0.0

            for source_product_id, weight in share_source_weights.items():
                if source_product_id == product_id:
                    raise HealthSynthConfigurationError(
                        f"products[{index}].share_source_weights cannot reference the same product."
                    )

                if weight < 0:
                    raise HealthSynthConfigurationError(
                        f"products[{index}].share_source_weights."
                        f"{source_product_id} must be greater than or equal to 0."
                    )

                total_weight += float(weight)

            if abs(total_weight - 1.0) > 0.01:
                raise HealthSynthConfigurationError(
                    f"products[{index}].share_source_weights "
                    "must sum to approximately 1.0. "
                    f"Current sum: {total_weight:.4f}"
                )

        if promotion_adoption_weight is not None and not 0 <= promotion_adoption_weight <= 1:
            raise HealthSynthConfigurationError(
                f"products[{index}].promotion_adoption_weight must be between 0 and 1."
            )

        if adoption_curve is not None and adoption_curve != "linear":
            raise HealthSynthConfigurationError(
                f"products[{index}].adoption_curve currently supports only 'linear'."
            )

        if adoption_months is not None and adoption_months <= 0:
            raise HealthSynthConfigurationError(
                f"products[{index}].adoption_months must be greater than 0."
            )

        if launch_share_factor is not None and not 0 <= launch_share_factor <= 1:
            raise HealthSynthConfigurationError(
                f"products[{index}].launch_share_factor must be between 0 and 1."
            )

        if adoption_curve is not None and adoption_months is None:
            raise HealthSynthConfigurationError(
                f"products[{index}].adoption_months is required when adoption_curve is configured."
            )

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

        seen_product_ids.add(product_id)

        all_product_ids = {product["product_id"] for product in products}

        product_area_lookup = {
            product["product_id"]: product.get(
                "therapeutic_area",
                "Unknown",
            )
            for product in products
        }

        for index, product in enumerate(products):
            product_id = product["product_id"]
            therapeutic_area = product.get(
                "therapeutic_area",
                "Unknown",
            )

            share_source_weights = product.get(
                "share_source_weights",
                {},
            )

            for source_product_id in share_source_weights:
                if source_product_id not in all_product_ids:
                    raise HealthSynthConfigurationError(
                        f"products[{index}].share_source_weights "
                        f"references unknown product "
                        f"'{source_product_id}'."
                    )

                if product_area_lookup[source_product_id] != therapeutic_area:
                    raise HealthSynthConfigurationError(
                        f"products[{index}].share_source_weights "
                        f"references product '{source_product_id}' "
                        "from a different therapeutic area."
                    )

    _validate_baseline_market_share(products)


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


def _validate_market(config: dict) -> None:
    market = config.get("market")

    if not market:
        raise HealthSynthConfigurationError("market configuration is required.")

    required_fields = ["market_id", "market_name", "country"]

    for field in required_fields:
        if not market.get(field):
            raise HealthSynthConfigurationError(f"market.{field} is required.")
