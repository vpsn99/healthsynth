from copy import deepcopy

REPLACE_KEYS = {
    "specialty_distribution",
    "decile_distribution",
    "channel_distribution",
    "channel_response_multiplier",
    "specialty_product_affinity",
}


def deep_merge(base: dict, override: dict | None) -> dict:
    result = deepcopy(base)

    if not override:
        return result

    for key, value in override.items():
        if key in REPLACE_KEYS:
            result[key] = deepcopy(value)
        elif key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result
