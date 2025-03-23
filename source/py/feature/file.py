from source.py.feature.utils import blk, cls, create_fea, lkup, subst

classes = {
    "zero": cls(name="zero", glyphs=["zero", "zero.zero"])
}
def generate_feature_file():
    return create_fea(
        classes=list(classes.values()),
        blocks=[
            blk("zero", [
                lkup("z", [
                    subst(
                        glyphs=["zero"],
                        replace="zero.zero"
                    )])
            ])
        ]
    )