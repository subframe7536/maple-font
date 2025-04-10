import re
import json
from source.py.feature import generate_fea_string, generate_fea_string_cn_only
from source.py.feature import (
    get_all_calt_text,
    get_cv_desc,
    get_cv_italic_desc,
    get_cv_cn_desc,
    get_ss_desc,
    get_total_feat,
)
from source.py.utils import joinPaths


def write_to_file(file_path: str, content: str, mode: str = "w") -> None:
    if not file_path or not isinstance(file_path, str):
        raise ValueError("Invalid file path. Please provide a valid string path.")
    if not isinstance(content, str):
        raise ValueError("Invalid content. Content must be a string.")

    with open(file_path, encoding="utf-8", mode=mode) as file:
        file.write(content)


BORDER_CALT = "<!-- CALT -->"
BORDER_CV = "<!-- CV -->"
BORDER_CV_IT = "<!-- CV-IT -->"
BORDER_CV_CN = "<!-- CV-CN -->"
BORDER_SS = "<!-- SS -->"


def replace_content(md_path: str, border: str, content: str):
    with open(md_path, "r", encoding="utf-8") as file:
        md_content = file.read()
    pattern = f"{border}(.*){border}"
    updated_content = re.sub(
        pattern, f"{border}\n{content}\n{border}", md_content, flags=re.DOTALL
    )

    write_to_file(md_path, updated_content)


def update_schema_freeze_options(schema_path: str, features: dict[str, str]):
    with open(schema_path, "r", encoding="utf-8") as file:
        schema = json.load(file)

    properties = {}

    for tag, desc in features.items():
        properties[tag] = {"description": desc, "$ref": "#/definitions/freeze_options"}

    schema["properties"]["feature_freeze"]["properties"] = properties

    with open(schema_path, "w", encoding="utf-8") as file:
        json.dump(schema, file, indent=2)


def update_config_feature_freeze(config_path: str, features: dict[str, str]):
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    feature_freeze = {}
    for tag in features.keys():
        feature_freeze[tag] = "ignore"

    config["feature_freeze"] = feature_freeze

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)


def update_normal_config_feature_freeze(config_path: str, features: dict[str, str]):
    normal_enable_keys = [
        "cv01",
        "cv02",
        "cv33",
        "cv34",
        "cv35",
        "cv36",
        "ss05",
        "ss06",
        "ss07",
        "ss08",
    ]
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    feature_freeze = {}
    for tag in features.keys():
        feature_freeze[tag] = "enable" if tag in normal_enable_keys else "ignore"

    config["feature_freeze"] = feature_freeze

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)


def fea(output: str):
    write_to_file(joinPaths(output, "regular.fea"), generate_fea_string(False, False))
    write_to_file(joinPaths(output, "italic.fea"), generate_fea_string(True, False))

    # write_to_file(joinPaths(output, "regular_cn.fea"), generate_fea_string(False, True))
    # write_to_file(joinPaths(output, "italic_cn.fea"), generate_fea_string(True, True))

    write_to_file(joinPaths(output, "cn.fea"), generate_fea_string_cn_only())

    md_path = joinPaths(output, "README.md")
    replace_content(
        md_path,
        BORDER_CALT,
        f"```\n{get_all_calt_text()}\n```",
    )
    replace_content(
        md_path,
        BORDER_CV,
        get_cv_desc(),
    )
    replace_content(
        md_path,
        BORDER_CV_IT,
        get_cv_italic_desc(),
    )
    replace_content(
        md_path,
        BORDER_CV_CN,
        get_cv_cn_desc(),
    )
    replace_content(
        md_path,
        BORDER_SS,
        get_ss_desc(),
    )

    features = get_total_feat()
    update_schema_freeze_options(joinPaths("source", "schema.json"), features)
    update_normal_config_feature_freeze(joinPaths("source", "preset-normal.json"), features)
    update_config_feature_freeze(joinPaths("config.json"), features)
