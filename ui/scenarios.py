from pathlib import Path
from typing import Any


def build_scenarios(
    repository_root: Path,
) -> dict[str, dict[str, Any]]:
    profiles_root = repository_root / "configs" / "profiles"

    return {
        "Default Market": {
            "path": None,
            "title": "Default Commercial Market",
            "description": (
                "Generate a general commercial analytics dataset "
                "using HealthSynth's built-in defaults."
            ),
            "question": (
                "What does a complete simulated pharmaceutical commercial market look like?"
            ),
            "event_label": None,
            "locality": {
                "label": "Canada",
                "faker_locale": "en_CA",
                "country_code": "CA",
            },
        },
        "Oncology Training": {
            "path": profiles_root / "oncology_training.yaml",
            "title": "Oncology Training Market",
            "description": (
                "Explore a stable oncology market containing mature "
                "products, HCP activity, demand, share, and prescriptions."
            ),
            "question": (
                "How do demand, promotion, market share, and "
                "prescriptions interact in a mature market?"
            ),
            "event_label": None,
            "locality": {
                "label": "Canada",
                "faker_locale": "en_CA",
                "country_code": "CA",
            },
        },
        "UK Oncology Training": {
            "path": profiles_root / "uk_oncology_training.yaml",
            "title": "UK Oncology Training Market",
            "description": (
                "Explore an oncology commercial market using "
                "United Kingdom-localized synthetic HCP identities."
            ),
            "question": (
                "How does the same commercial market look when its "
                "synthetic identities are localized for the UK?"
            ),
            "event_label": None,
            "locality": {
                "label": "United Kingdom",
                "faker_locale": "en_GB",
                "country_code": "GB",
            },
        },
        "Japan Oncology Training": {
            "path": profiles_root / "japan_oncology_training.yaml",
            "title": "Japan Oncology Training Market",
            "description": (
                "Explore an oncology commercial market using "
                "Japan-localized synthetic HCP identities."
            ),
            "question": (
                "How does the same commercial market look when its "
                "synthetic identities are localized for Japan?"
            ),
            "event_label": None,
            "locality": {
                "label": "Japan",
                "faker_locale": "ja_JP",
                "country_code": "JP",
            },
        },
        "New Product Launch": {
            "path": profiles_root / "oncology_product_launch.yaml",
            "title": "New Product Launch",
            "description": (
                "Introduce a new oncology product and observe its "
                "gradual adoption, promotional acceleration, and "
                "impact on incumbent products."
            ),
            "question": (
                "How does a newly launched product gain share from established competitors?"
            ),
            "event_label": "Product launch",
            "locality": {
                "label": "Canada",
                "faker_locale": "en_CA",
                "country_code": "CA",
            },
        },
        "Loss of Exclusivity": {
            "path": profiles_root / "oncology_loe.yaml",
            "title": "Loss of Exclusivity",
            "description": (
                "Model the erosion of an established product after "
                "loss of exclusivity and the redistribution of its share."
            ),
            "question": (
                "What happens to market share and prescriptions "
                "after an established brand loses exclusivity?"
            ),
            "event_label": "LOE",
            "locality": {
                "label": "Canada",
                "faker_locale": "en_CA",
                "country_code": "CA",
            },
        },
        "Competitor Launch": {
            "path": profiles_root / "oncology_competitor_launch.yaml",
            "title": "Competitor Launch",
            "description": (
                "Add a new competitor to an established oncology "
                "market and observe how incumbents respond."
            ),
            "question": ("How does competitor entry change the balance of an existing market?"),
            "event_label": "Competitor launch",
            "locality": {
                "label": "Canada",
                "faker_locale": "en_CA",
                "country_code": "CA",
            },
        },
        "Market Access": {
            "path": profiles_root / "oncology_market_access.yaml",
            "title": "Market Access Change",
            "description": (
                "Apply an access improvement to one product and "
                "observe how commercial opportunity and prescription "
                "allocation change."
            ),
            "question": (
                "Can improved access increase prescriptions without changing total market demand?"
            ),
            "event_label": "Access change",
            "locality": {
                "label": "Canada",
                "faker_locale": "en_CA",
                "country_code": "CA",
            },
        },
    }
