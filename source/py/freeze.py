from source.py.in_browser import (
    freeze_feature as freeze,
    get_freeze_config_str as config_str,
)
from fontTools.ttLib import TTFont


def is_enable(v):
    return v.upper().startswith("ENABLE")


def is_disable(v):
    return v.upper().startswith("DISABLE")


def is_ignore(v):
    return v.upper().startswith("IGNORE")


def patch_config(config: dict, calt: bool):
    result = {}
    invalid_items = []
    for k, v in config.items():
        if is_enable(v):
            result[k] = "1"
        elif is_disable(v):
            result[k] = "-1"
        elif not is_ignore(v):
            invalid_items.append((k, v))
        else:
            result[k] = "0"

    if len(invalid_items) > 0:
        report = ", ".join([f"{k}: {v}" for k, v in invalid_items])
        raise TypeError(f"Invalid freeze config item: {{ {report} }}")

    result["calt"] = "1" if calt else "0"

    return result


def get_freeze_config_str(config: dict, calt: bool) -> str:
    return config_str(patch_config(config, calt))


def freeze_feature(font: TTFont, calt: bool, moving_rules: list[str], config: dict):
    return freeze(font, moving_rules, patch_config(config, calt))
