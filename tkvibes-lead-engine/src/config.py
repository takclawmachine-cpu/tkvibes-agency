"""Config loader with startup validation and safe defaults."""

import os
import sys
import yaml

REQUIRED_CONFIG_KEYS = {
    "run": ["collect_personal_data", "cache_stale_days", "max_leads_per_run"],
    "sources": ["google_places"],
    "targets": ["cities", "categories", "max_results_per_query"],
    "scoring": ["high_fit_categories"],
    "sheets": ["worksheet_name"],
    "handoff": ["export_json", "min_tier"],
}

SECRETS_IN_CONFIG = [
    "api_key",
]


def _check_secrets_in_config(cfg: dict, path: str = ""):
    """Warn if API keys/secrets are found in config.yaml instead of env vars."""
    for key in SECRETS_IN_CONFIG:
        if path == "crm" and key in cfg.get("crm", {}):
            val = cfg["crm"].get(key, "")
            if val and not val.startswith("${"):
                print(
                    f"  ⚠️  SECURITY: API key found in config.yaml (crm.{key}). "
                    f"Move it to .env as a env var instead."
                )


def load_config(path: str = "config.yaml") -> dict:
    """Load YAML config with validation.

    Raises FileNotFoundError, ValueError, yaml.YAMLError on failure.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Config not found: {path}\n"
            f"Copy config.yaml.example to config.yaml and fill in your settings."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}") from e

    if not isinstance(cfg, dict):
        raise ValueError(f"Config must be a dictionary, got {type(cfg).__name__}")

    # Validate required top-level sections and keys
    for section, keys in REQUIRED_CONFIG_KEYS.items():
        if section not in cfg:
            raise ValueError(f"Missing required config section: '{section}'")
        section_cfg = cfg[section] or {}
        if isinstance(section_cfg, dict):
            for key in keys:
                if key not in section_cfg:
                    raise ValueError(
                        f"Missing required config key: '{section}.{key}'"
                    )

    # Validate targets are non-empty
    if not cfg.get("targets", {}).get("cities"):
        raise ValueError("config.yaml: 'targets.cities' must have at least one city")
    if not cfg.get("targets", {}).get("categories"):
        raise ValueError(
            "config.yaml: 'targets.categories' must have at least one category"
        )

    _check_secrets_in_config(cfg)

    return cfg