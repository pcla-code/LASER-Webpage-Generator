import pandas as pd, re, html
df = pd.read_csv(r"../ies problems and answer parts.csv")
g = df[df.problem_set_xref=="PSBGCK8"]
for po, gg in g.groupby('problem_order'):
    r = gg.iloc[0]
    print("="*70)
    print(f"order={po} problem_xref={r['problem_xref']} part={r['problem_part']}")
    print("ANSWER:", repr(r['correct_answer']))
    print("BODY RAW:")
    print(str(r['problem_body']))
    print()
