"""Verification/analysis of IES module->assignment mapping vs source CSV vs generated pages."""
import os, re, glob
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "IES")
OUT = os.path.join(os.path.dirname(__file__), "_analysis_report.txt")
gen_dir = os.path.join(BASE, "IES-DLP-generated-webpages")

lines = []
def p(*a):
    lines.append(" ".join(str(x) for x in a))

# 1. Excel module mapping
xl = pd.read_excel(os.path.join(BASE, "ASSISTment IDs updated.xlsx"),
                   sheet_name="fall 2026", header=0)
cols = list(xl.columns)
p("EXCEL COLUMNS:", cols)
# The name column and problem columns: find 'Name' col and the numbered problem cols
# Based on structure: col indices -> Module(New), Module(Old), ?, Name, Instructor, Original/Copy, then 1..39
p("=== MODULE MAPPING (from Excel) ===")
module_map = {}  # module_name -> list of problem_xref
for _, row in xl.iterrows():
    vals = list(row.values)
    name = None
    # find the name: it's the first long text cell
    # columns: 0 Module(New),1 Module(Old),2 ?,3 Name,4 Instructor,5 Original vs copy, 6.. problems
    name = vals[3]
    probs = []
    for v in vals[6:]:
        if isinstance(v, str) and v.strip() and v.strip() != 'nan':
            probs.append(v.strip())
    if isinstance(name, str) and name.strip():
        module_map[name.strip()] = probs
        p(f"- {name.strip()} :: {probs}")

# 2. Original source CSV
src = pd.read_csv(os.path.join(BASE, "ies problems and answer parts.csv"))
p("\n=== SOURCE CSV COLUMNS ===")
p(list(src.columns))
p("Unique problem_set_xref:", sorted(src['problem_set_xref'].dropna().unique().tolist()))

# Map problem_xref -> problem_set_xref, order, parts
p("\n=== problem_set -> problems (order) from source ===")
for ps, grp in src.groupby('problem_set_xref'):
    prob_order = grp.drop_duplicates('problem_xref')[['problem_xref','problem_order']]
    items = sorted(prob_order.values.tolist(), key=lambda x: int(x[1]))
    p(f"{ps}: {[i[0] for i in items]}")

# 3. For each module, check which problem_set each problem belongs to
p("\n=== MODULE problems -> source coverage ===")
prob_to_ps = {}
for _, r in src.iterrows():
    prob_to_ps.setdefault(r['problem_xref'], r['problem_set_xref'])
for mod, probs in module_map.items():
    missing = [x for x in probs if x not in prob_to_ps]
    pss = sorted(set(prob_to_ps.get(x,'??') for x in probs))
    p(f"- {mod}: problem_sets={pss} missing_from_source={missing}")

# 4. Generated pages inventory: first page per problem_set code in filename
p("\n=== GENERATED first-pages per code ===")
files = [os.path.basename(f) for f in glob.glob(os.path.join(gen_dir, "*.html"))]
firsts = {}
for f in files:
    m = re.match(r"(CPS[AB])-([A-Z0-9]+)-Q(\d+)-", f)
    if m and m.group(3) == "1":
        firsts[m.group(2)] = f
for code in sorted(firsts):
    p(f"{code}: {firsts[code]}")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("WROTE", OUT, "lines", len(lines))
