import pandas as pd, re, html, textwrap
df = pd.read_csv(r"IES/ies problems and answer parts.csv")

def show(ps):
    g = df[df.problem_set_xref==ps]
    print("="*80)
    print("PROBLEM SET", ps, " rows:", len(g))
    for po, gg in g.groupby('problem_order'):
        r = gg.iloc[0]
        body = str(r['problem_body'])
        print("-"*70)
        print(f"order={po} problem_xref={r['problem_xref']} part={r['problem_part']}")
        print("ANSWER:", repr(r['correct_answer']))
        print("BODY RAW:")
        print(body[:1600])
        print()

import sys
for ps in sys.argv[1:]:
    show(ps)
