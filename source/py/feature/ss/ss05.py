from source.py.feature import ast


def ss05_subst():
    return [ast.subst_map("\\", source_suffix=".liga")]


ss05_name = 'Revert thin backslash in escape symbols (`\\\\`, `\\"`, `\\.` ...)'
ss05_feat = ast.StylisticSet(
    id=5, desc=ss05_name, content=ss05_subst(), version="7.0", example="\\\\"
)
