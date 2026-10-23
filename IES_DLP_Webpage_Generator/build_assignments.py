"""
build_assignments.py
--------------------
Rebuilds the IES assignment webpages directly from the source-of-truth CSV
(`IES/ies problems and answer parts.csv`) and fixes the structural bugs:

  * Groups questions by the TRUE assignment id (problem_set_xref) so every
    problem/part in a module chains into ONE flow that ends with a single
    completion-code page (previously each problem became its own mini-assignment
    that dead-ended on a completion page).
  * Orders questions by problem_order / part, collecting all authored hints.
  * Cleans HTML markup and special characters from question/answer/hint text.

It then emits an intermediate CSV in the column format WebpageGenerator3 expects
and invokes that generator, writing chained pages into IES-DLP-generated-webpages/.

Finally it prints the first-page filename for each assignment so digital_training.html
can be linked accurately.
"""
import os
import re
import csv
import glob
import html as _html
import pandas as pd

import WebpageGenerator3 as wg

BASE = os.path.dirname(__file__)
IES = os.path.join(BASE, "IES")
SRC = os.path.join(IES, "ies problems and answer parts.csv")
OUT_DIR = os.path.join(IES, "IES-DLP-generated-webpages")
INTERMEDIATE = os.path.join(IES, "ies-problems-formatted.csv")


# ── text cleaning ────────────────────────────────────────────────────────────

_CELL_RE = re.compile(r"<t([dh])\b[^>]*>(.*?)</t\1>", re.IGNORECASE | re.DOTALL)
_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_TABLE_RE = re.compile(r"<table\b[^>]*>(.*?)</table>", re.IGNORECASE | re.DOTALL)


def _strip_inline(s: str) -> str:
    """Remove inline tags from a small fragment (e.g. a table cell) and tidy text."""
    s = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    s = _html.unescape(s).replace("\xa0", " ")
    s = (s.replace("\u2018", "'").replace("\u2019", "'")
           .replace("\u201c", '"').replace("\u201d", '"')
           .replace("\u2013", "-").replace("\u2014", "-"))
    return re.sub(r"\s+", " ", s).strip()


def _convert_table(table_html: str) -> str:
    """Convert a source <table> into a clean, styled single-line HTML table.

    Emitted on ONE line (no newlines) so the generator's \\n -> <br> step leaves
    it intact. The first row is treated as a header when it uses <th> or when any
    cell is empty / bold (typical of these quiz tables)."""
    rows = []
    for rm in _ROW_RE.finditer(table_html):
        cells = [(tag.lower(), _strip_inline(content))
                 for tag, content in _CELL_RE.findall(rm.group(1))]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    # Decide if first row is a header: it has <th>, or a leading empty corner cell
    first_is_header = (
        any(tag == "h" for tag, _ in rows[0])
        or (len(rows) > 1 and rows[0] and rows[0][0][1] == "")
    )
    style_tbl = ('style="border-collapse:collapse;margin:14px 0;" border="1"')
    style_cell = ('style="border:1px solid #bbb;padding:6px 12px;text-align:left;"')
    out = [f'<table {style_tbl}>']
    for ri, row in enumerate(rows):
        out.append("<tr>")
        for tag, text in row:
            is_head = first_is_header and ri == 0
            cell_tag = "th" if (is_head or tag == "h") else "td"
            extra = ' style="border:1px solid #bbb;padding:6px 12px;background:#f0f4ff;text-align:left;"' if cell_tag == "th" else f" {style_cell}"
            out.append(f"<{cell_tag}{extra}>{text}</{cell_tag}>")
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)


def clean_html(raw: str) -> str:
    """Convert an HTML fragment to readable text, preserving real tables as HTML."""
    if raw is None:
        return ""
    s = str(raw)

    # 1. Protect tables: convert to clean single-line HTML and stash behind tokens
    tables = []

    def _stash(m):
        tables.append(_convert_table(m.group(1)))
        return f"\n\x00TABLE{len(tables) - 1}\x00\n"

    s = _TABLE_RE.sub(_stash, s)

    # 2. Normal text cleaning
    # Links -> keep visible text
    s = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", s, flags=re.IGNORECASE | re.DOTALL)
    # List items -> "- item"
    s = re.sub(r"<li\b[^>]*>", "\n- ", s, flags=re.IGNORECASE)
    # Block breaks
    s = re.sub(r"</(p|div|h\d|ul|ol)>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    # Drop all remaining tags
    s = re.sub(r"<[^>]+>", "", s)
    # Unescape entities (&nbsp; &ldquo; etc.)
    s = _html.unescape(s)
    s = s.replace("\xa0", " ")
    # Normalise curly quotes/dashes
    s = (s.replace("\u2018", "'").replace("\u2019", "'")
           .replace("\u201c", '"').replace("\u201d", '"')
           .replace("\u2013", "-").replace("\u2014", "-"))
    # Collapse whitespace while preserving paragraph breaks
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")]
    out, blank = [], False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    result = "\n".join(out).strip()

    # 3. Restore tables
    for i, tbl in enumerate(tables):
        result = result.replace(f"\x00TABLE{i}\x00", tbl)
    return result


def parse_pg_array(raw: str) -> list:
    """Parse a Postgres text[] literal like {a,"b c","he said \"hi\""} -> list."""
    if raw is None or str(raw).strip().upper() == "NULL":
        return []
    s = str(raw).strip()
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    out, buf, in_q, i = [], [], False, 0
    while i < len(s):
        ch = s[i]
        if ch == '"':
            if in_q and i + 1 < len(s) and s[i + 1] == '"':
                buf.append('"'); i += 2; continue
            in_q = not in_q; i += 1; continue
        if ch == "\\" and i + 1 < len(s):
            buf.append(s[i + 1]); i += 2; continue
        if ch == "," and not in_q:
            out.append("".join(buf)); buf = []; i += 1; continue
        buf.append(ch); i += 1
    if buf or out:
        out.append("".join(buf))
    return [clean_html(_html.unescape(x)).strip() for x in out if x.strip() != ""]


# ── curriculum prefix (CPSA / CPSB) ──────────────────────────────────────────

def curriculum_for(problem_set_xref: str) -> str:
    """Reproduce the original CPSA/CPSB prefix derived from the problem_set id."""
    # generate_filename does "C" + curriculum[:3].upper(); PSA* -> CPSA, PSB* -> CPSB
    return problem_set_xref


# ── multiple-choice option inference ─────────────────────────────────────────

# Standard closed-domain option sets used by the "check your understanding"
# questions. The source CSV stores only the correct answer (no distractors), so
# genuine multiple-choice items otherwise fall back to a free-text box whose only
# bottom-out hint reveals the answer. We reconstruct the full choice list here so
# these render as real multiple-choice questions.
_FEATURE_SET_OPTIONS = [
    'I should use "selected" features that are not highly correlated',
    'I should use all features; this model is not sensitive to multicollinearity',
]
_METRIC_VOCAB = ["AUC", "Cohen's Kappa", "Accuracy", "Recall", "Precision", "F1"]


def infer_options(question: str, answers: list) -> list:
    """Return the full displayed choice list for a known closed-domain MC item,
    or [] when we cannot confidently reconstruct the distractors."""
    if not answers:
        return []
    ans_set = {a.strip() for a in answers}
    q = question or ""

    # 1. Model 1 / Model 2 comparison questions
    if ans_set <= {"Model 1", "Model 2"} and "Model 1" in q and "Model 2" in q:
        return ["Model 1", "Model 2"]

    # 2. Feature-set selection questions
    if any("features" in a.lower() and (
            "correlated" in a.lower() or "multicollinearity" in a.lower())
           for a in answers):
        opts = list(_FEATURE_SET_OPTIONS)
        for a in answers:  # make sure the exact correct string is present
            if a not in opts:
                opts.append(a)
        return opts

    # 3. Metric-choice questions ("which metric provides the most useful info")
    if ans_set <= set(_METRIC_VOCAB) and "metric" in q.lower():
        present = [m for m in _METRIC_VOCAB if m in q]
        for a in answers:
            if a not in present:
                present.append(a)
        if len(present) >= 2:
            return present

    return []


# ── build intermediate CSV ───────────────────────────────────────────────────

def build_intermediate() -> list:
    df = pd.read_csv(SRC)
    rows = []            # intermediate CSV rows
    order_index = []     # preserve assignment order of first appearance
    seen_ps = set()

    # One "question" per (problem_set, problem_order).  problem_order is unique and
    # ordered within a problem_set and already accounts for multi-part problems.
    for ps, grp in df.groupby("problem_set_xref", sort=False):
        if ps not in seen_ps:
            order_index.append(ps); seen_ps.add(ps)

    assignments = {}  # ps -> list of question dicts
    for ps in order_index:
        grp = df[df["problem_set_xref"] == ps]
        questions = {}
        for _, r in grp.iterrows():
            key = int(r["problem_order"])
            q = questions.setdefault(key, {
                "question": clean_html(r["problem_body"]),
                "answers": parse_pg_array(r["correct_answer"]),
                "hints": {},
            })
            # keep the fullest question body
            qb = clean_html(r["problem_body"])
            if len(qb) > len(q["question"]):
                q["question"] = qb
            if not q["answers"]:
                q["answers"] = parse_pg_array(r["correct_answer"])
            hn, ht = r.get("hint_number"), r.get("hint_text")
            if pd.notna(hn) and pd.notna(ht) and str(ht).strip().upper() != "NULL":
                q["hints"][int(hn)] = clean_html(ht)
        assignments[ps] = [questions[k] for k in sorted(questions)]

    # Flatten to intermediate CSV rows (Curriculum, Problem Set, Question, Answer, Hint)
    for ps in order_index:
        for q in assignments[ps]:
            first = True
            hints = [q["hints"][k] for k in sorted(q["hints"])]
            answers = q["answers"] if q["answers"] else [""]
            options = infer_options(q["question"], q["answers"])
            opts_str = "|".join(options) if options else ""
            max_len = max(len(answers), len(hints), 1)
            for i in range(max_len):
                rows.append({
                    "Curriculum": ps if first else "",
                    "Problem Set": ps if first else "",
                    "Question": q["question"] if first else "",
                    "Answer": answers[i] if i < len(answers) else "",
                    "Options": opts_str if first else "",
                    "Hint": hints[i] if i < len(hints) else "",
                })
                first = False
    return rows, order_index


def main():
    rows, order_index = build_intermediate()

    # Write the cleaned intermediate CSV (same name the project already uses)
    with open(INTERMEDIATE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Curriculum", "Problem Set", "Question", "Answer", "Options", "Hint"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("Wrote intermediate CSV:", INTERMEDIATE, "rows:", len(rows))

    # Clear old generated pages so there are no stale per-problem mini-assignments
    for f in glob.glob(os.path.join(OUT_DIR, "*.html")):
        os.remove(f)

    # Generate chained pages (one completion page per assignment)
    wg.generate_webpages_from_csv(INTERMEDIATE, OUT_DIR)

    # Report the first-page filename for each assignment
    print("\n=== FIRST PAGE PER ASSIGNMENT ===")
    for ps in order_index:
        matches = glob.glob(os.path.join(OUT_DIR, f"CPS*-{ps}-Q1-*.html"))
        name = os.path.basename(matches[0]) if matches else "??? NOT FOUND"
        print(f"{ps}: {name}")

    relink_digital_training()


# ── relink digital_training.html ─────────────────────────────────────────────

# Maps each course module (by its "Module N:" heading) to the true source
# assignment id (problem_set_xref). Modules 6 (Ethics) and 11 (NLP) have no
# assignment in the source data, matching the Excel "Fall 2026" sheet.
MODULE_TO_PS = {
    1:  "PSABX638",   # Introduction, Challenges, and Framework
    2:  "PSBKJEF",    # Data and Measurement Validity
    3:  "PSABX64S",   # Feature Extraction and Feature Engineering
    4:  "PSABX64D",   # Prediction Modeling and Metrics
    5:  "PSBKJEN",    # Causal Reasoning
    7:  "PSABX65M",   # Cluster Analysis
    8:  "PSBFYED",    # Network Analysis
    9:  "PSABX65E",   # Sequential Pattern Mining and Temporal Analysis
    10: "PSABX64F",   # Neural Networks and Deep Learning
    12: "PSBJ6XU",    # Transformer and Foundation Models
    13: "PSBKAV5",    # Knowledge Tracing
    14: "PSBKJED",    # Knowledge Graphs
    15: "PSBGCK8",    # Data Visualization
    16: "PSBKJD8",    # Data Management and Database Access
}

DIGITAL_TRAINING = os.path.join(IES, "digital_training.html")
LINK_DIR = "IES-DLP-generated-webpages"


def relink_digital_training():
    with open(DIGITAL_TRAINING, "r", encoding="utf-8") as f:
        html_text = f.read()

    # Resolve each module's first-page filename
    first_page = {}
    for mod, ps in MODULE_TO_PS.items():
        matches = sorted(glob.glob(os.path.join(OUT_DIR, f"CPS*-{ps}-Q1-*.html")))
        if matches:
            first_page[mod] = os.path.basename(matches[0])

    # Split the document into per-module blocks on "<p><b>Module N:"
    module_re = re.compile(r"(<p><b>Module\s+(\d+):)")
    parts = module_re.split(html_text)
    # parts = [prefix, full_marker, num, block_body, full_marker, num, block_body, ...]
    # NOTE: full_marker already contains the number (e.g. "<p><b>Module 1:"), so the
    # separate `num` token must NOT be re-appended, or the number duplicates each run.
    rebuilt = [parts[0]]
    i = 1
    changed = 0
    while i < len(parts):
        marker, num, body = parts[i], int(parts[i + 1]), parts[i + 2]
        if num in first_page:
            new_href = f"{LINK_DIR}/{first_page[num]}"
            # Replace the first assignment link in this module block
            body, n = re.subn(
                r'(Assignment contents:\s*<a href=")[^"]*(">\[link\]</a>)',
                lambda m: m.group(1) + new_href + m.group(2),
                body, count=1,
            )
            changed += n
        rebuilt.append(marker)   # marker already includes the module number
        rebuilt.append(body)
        i += 3

    with open(DIGITAL_TRAINING, "w", encoding="utf-8") as f:
        f.write("".join(rebuilt))
    print(f"\nRelinked digital_training.html ({changed} module link(s) updated)")


if __name__ == "__main__":
    main()
