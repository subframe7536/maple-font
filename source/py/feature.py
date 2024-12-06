def get_freeze_config_str(feature_freeze, enable_liga):
    result = ""
    for k, v in feature_freeze.items():
        if v == "enable":
            result += f"+{k};"
        elif v == "disable":
            result += f"-{k};"
    if not enable_liga:
        result += "-calt;"
    return result

def freeze_feature(font, calt, moving_rules=[], config={}):
    # check feature list
    feature_record = font["GSUB"].table.FeatureList.FeatureRecord
    feature_dict = {
        feature.FeatureTag: feature.Feature
        for feature in feature_record
        if feature.FeatureTag != "calt"
    }

    if calt:
        calt_features = [
            feature.Feature for feature in feature_record if feature.FeatureTag == "calt"
        ]
    else:
        for feature in feature_record:
            if feature.FeatureTag == "calt":
                feature.Feature.LookupListIndex.clear()
                feature.Feature.LookupCount = 0
                feature.FeatureTag = "DELT"

    # Process features
    for tag, status in config.items():
        target_feature = feature_dict.get(tag)
        if not target_feature or status == "ignore":
            continue

        if status == "disable":
            target_feature.LookupListIndex = []
            continue

        if tag in moving_rules and calt:
            # Enable by moving rules into "calt"
            for calt_feat in calt_features:
                calt_feat.LookupListIndex.extend(target_feature.LookupListIndex)
        else:
            # Enable by replacing data in glyf and hmtx tables
            glyph_dict = font["glyf"].glyphs
            hmtx_dict = font["hmtx"].metrics
            for index in target_feature.LookupListIndex:
                lookup_subtable = font["GSUB"].table.LookupList.Lookup[index].SubTable[0]
                if not lookup_subtable or "mapping" not in lookup_subtable.__dict__:
                    continue
                for old_key, new_key in lookup_subtable.mapping.items():
                    if (
                        old_key in glyph_dict
                        and old_key in hmtx_dict
                        and new_key in glyph_dict
                        and new_key in hmtx_dict
                    ):
                        glyph_dict[old_key] = glyph_dict[new_key]
                        hmtx_dict[old_key] = hmtx_dict[new_key]
                    else:
                        print(f"{old_key} or {new_key} does not exist")
                        return
