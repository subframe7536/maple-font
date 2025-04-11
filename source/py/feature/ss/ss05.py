from source.py.feature import ast


def ss05_subst():
    return [ast.subst_map("\\", source_suffix=".liga")]


ss05_name = 'Revert thin backslash in escape symbols (`\\\\`, `\\"`, `\\.` ...)'
ss05_feat = ast.StylisticSet(5, ss05_name, ss05_subst())
