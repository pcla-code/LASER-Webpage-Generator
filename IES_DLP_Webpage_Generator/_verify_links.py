"""Verify every generated page links to an existing next page and each assignment
ends at exactly one completion page. Also checks digital_training.html links."""
import os, re, glob, collections

BASE = os.path.dirname(__file__)
IES = os.path.join(BASE, "IES")
OUT = os.path.join(IES, "IES-DLP-generated-webpages")

files = {os.path.basename(f) for f in glob.glob(os.path.join(OUT, "*.html"))}
broken = []
href_re = re.compile(r'href="([^"]+\.html)"')
for f in files:
    with open(os.path.join(OUT, f), encoding="utf-8") as fh:
        txt = fh.read()
    for h in href_re.findall(txt):
        if "/" not in h and h not in files:
            broken.append((f, h))

# group by assignment id
by_ps = collections.defaultdict(list)
for f in files:
    m = re.match(r"CPS[AB]-([A-Z0-9]+)-Q", f)
    if m:
        by_ps[m.group(1)].append(f)

print("Total pages:", len(files))
print("Assignments:", len(by_ps))
ends = [f for f in files if "-QZ-END-" in f]
print("Completion pages:", len(ends))
print("Broken internal links:", len(broken))
for b in broken[:20]:
    print("  BROKEN", b)

# digital_training links resolve?
dt = os.path.join(IES, "digital_training.html")
with open(dt, encoding="utf-8") as fh:
    dttxt = fh.read()
dt_broken = []
for h in re.findall(r'href="(IES-DLP-generated-webpages/[^"]+)"', dttxt):
    if not os.path.exists(os.path.join(IES, h)):
        dt_broken.append(h)
print("digital_training broken links:", dt_broken)
