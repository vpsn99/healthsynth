from copy import deepcopy


def deep_merge(base: dict, override: dict | None) -> dict:
    """
    Recursively merge override into base.

    Values from override win.
    Nested dictionaries are merged.
    Lists are replaced, not merged.
    """
    result = deepcopy(base)

    if not override:
        return result

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result
