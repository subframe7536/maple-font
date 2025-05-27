from source.py.feature import ast


class Seq:
    def __init__(self, g: str | list[str]) -> None:
        self.src = g[0]
        self.sta = ast.gly_seq(g, "sta")
        self.mid = ast.gly_seq(g, "mid")
        self.end = ast.gly_seq(g, "end")

# lookup equal_arrows {
#   # Disable |||
#   ignore sub bar bar' bar equal;
#   ignore sub bar bar' equal;
#   ignore sub [equal.sta.seq equal.mid.seq] bar' bar bar;

#   # equal middle & end
#   sub [less_equal.sta.seq less_equal.mid.seq equal.sta.seq equal.mid.seq] equal' [equal less] by equal.mid.seq;

#   sub [less_equal.sta.seq less_equal.mid.seq equal.sta.seq equal.mid.seq] equal' by equal.end.seq;

#   # single middles
#   sub [equal.sta.seq equal.mid.seq] less'    equal by less_equal.mid.seq;

#   # single ends
#   sub [equal.sta.seq equal.mid.seq] less'    by less_equal.end.seq;

#   # Disable >=< #548
#   sub greater' equal less [equal less] by greater_equal.sta.seq;
#   ignore sub greater' equal less;

#   # Disable =< #479 #468 #424 #406 #355 #305
#   sub equal' less [equal less] by equal.sta.seq;

#   # Disable =/ #1056
#   sub equal'   slash [equal slash] by equal.sta.seq;

#   # single beginnings
#   sub less'    equal by less_equal.sta.seq;

# } equal_arrows;

def lookup_seq(g: str):
    seq = Seq(g)
    less = Seq(["<", g])
    g_start = ast.cls(seq.sta, seq.mid)
    return (
        ast.Lookup(
            "infinity_" + ast.gly(g),
            "".join([g] * 4),
            [
                # less
                ast.subst(None, less.src, [seq.src, seq.src], less.sta),
                ast.subst(less.sta, seq.src, seq.src, seq.mid),
                ast.subst(g_start, seq.src, less.src, seq.mid),
                ast.subst([g_start, seq.mid], less.src, None, less.end),
                ast.subst(seq.mid, less.src, seq.src, less.mid),
                ast.subst(None, seq.src, [less.src, seq.src], seq.sta),
                ast.subst(g_start, less.src, seq.src, less.mid),
                ast.subst(less.mid, seq.src, seq.src, seq.mid),
                # source
                ast.subst(g_start, seq.src, seq.src, seq.mid),
                ast.subst(g_start, seq.src, None, seq.end),
                ast.subst(None, seq.src, seq.src, seq.sta),
            ],
        ),
    )


def ss12_subst():
    return [
        lookup_seq("="),
        # lookup_seq("-"),
    ]


ss12_name = "Infinite hyphens and equals (`----`, `====`)"
ss12_feat = ast.StylisticSet(
    id=12, desc=ss12_name, content=ss12_subst(), version="7.3", sample="===="
)
