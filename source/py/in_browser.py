import io
import json
from zipfile import ZipFile
from fontTools.ttLib import TTFont

MOVING_RULES = ["ss03", "ss07", "ss08", "ss09", "ss10", "ss11"]


def get_freeze_config_str(config):
    result = ""
    for k, v in sorted(config.items()):
        if v == "1":
            result += f"+{k};"
        if v == "0" and k == "calt" or v == "-1":
            result += f"-{k};"
    return result


def freeze_feature(font, moving_rules, config):
    feature_list = font["GSUB"].table.FeatureList
    feature_record = feature_list.FeatureRecord
    feature_dict = {
        feature.FeatureTag: (i, feature.Feature)
        for i, feature in enumerate(feature_record)
        if feature.FeatureTag != "calt"
    }

    calt_features = [
        feature.Feature for feature in feature_record if feature.FeatureTag == "calt"
    ]

    enable_calt = config.get("calt") == "1"
    if not enable_calt:
        for calt_feature in calt_features:
            calt_feature.LookupListIndex.clear()
            calt_feature.LookupCount = 0

    indices_to_remove = []
    for tag, status in config.items():
        if tag not in feature_dict or status == "0":
            continue

        index, target_feature = feature_dict[tag]
        if status == "-1":
            indices_to_remove.append(index)
            continue

        if tag in moving_rules and enable_calt:
            for calt_feature in calt_features:
                calt_feature.LookupListIndex.extend(target_feature.LookupListIndex)
        else:
            glyph_dict = font["glyf"].glyphs
            hmtx_dict = font["hmtx"].metrics
            for lookup_index in target_feature.LookupListIndex:
                mapping = getattr(
                    font["GSUB"].table.LookupList.Lookup[lookup_index].SubTable[0],
                    "mapping",
                    None,
                )
                if not mapping:
                    continue
                for old_key, new_key in mapping.items():
                    if (
                        old_key in glyph_dict
                        and old_key in hmtx_dict
                        and new_key in glyph_dict
                        and new_key in hmtx_dict
                    ):
                        glyph_dict[old_key] = glyph_dict[new_key]
                        hmtx_dict[old_key] = hmtx_dict[new_key]

    # Remove features's lookup list index in reverse order to maintain correct indices
    for index in sorted(indices_to_remove, reverse=True):
        feature_list.FeatureRecord[index].Feature.LookupCount = 0
        feature_list.FeatureRecord[index].Feature.LookupListIndex = []


def set_font_name(font, name: str, id: int):
    font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)


def get_font_name(font, id: int) -> str:
    return (
        font["name"]
        .getName(nameID=id, platformID=3, platEncID=1, langID=0x409)
        .__str__()
    )


def main(zip_path: str, target_path: str, config: dict):
    with (
        ZipFile(zip_path, "r") as zip_in,
        ZipFile(target_path, "w") as zip_out,
    ):
        for file_info in zip_in.infolist():
            file_name = file_info.filename
            if file_name.lower().endswith((".ttf", ".otf")):
                print(f"Patch: {file_name}")
                with zip_in.open(file_info) as ttf_file:
                    font = TTFont(ttf_file)

                    suffix = get_freeze_config_str(config)
                    freeze_feature(font, MOVING_RULES, config)
                    set_font_name(font, get_font_name(font, 3) + suffix, 3)

                    output_io = io.BytesIO()
                    font.save(output_io)
                    output_io.seek(0)
                    zip_out.writestr(file_info, output_io.read())
                    font.close()
            else:
                print(f"Skip:  {file_name}")
                zip_out.writestr(file_info, zip_in.read(file_info))

        zip_out.writestr(
            "patch-in-browser.json",
            json.dumps(
                {k: "freeze" if v == "1" else "ignore" for k, v in config.items()},
                indent=4,
            ),
        )
        print("Write: patch-in-browser.json")

    print("Repack zip")
