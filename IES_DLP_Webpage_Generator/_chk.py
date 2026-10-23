import os, re, glob
IES = "IES"
OUT = os.path.join(IES, "IES-DLP-generated-webpages")
files = {os.path.basename(f) for f in glob.glob(os.path.join(OUT, "*.html"))}
hr = re.compile(r'href="([^"]+\.html)"')
broken = []
for f in files:
    for h in hr.findall(open(os.path.join(OUT, f), encoding="utf-8").read()):
        if "/" not in h and h not in files:
            broken.append((f, h))
dt = open(os.path.join(IES, "digital_training.html"), encoding="utf-8").read()
dtb = [h for h in re.findall(r'href="(IES-DLP-generated-webpages/[^"]+)"', dt)
       if not os.path.exists(os.path.join(IES, h))]
print("pages", len(files), "broken", len(broken), "dt_broken", dtb)
