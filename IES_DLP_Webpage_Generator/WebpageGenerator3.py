"""
WebpageGenerator3.py — improved LASER webpage generator.

Fixes over LASERWebpageGenerator2.py:
  1. Filenames use the full problem-set ID, not just the first 3 chars — eliminates
     the collision where PRABU5RA/PRABU5RB/PRABU5RC all become PSPRA.
  2. Supports an optional 'Options' column (pipe-separated, e.g. "A|B|C|D") for
     proper multiple-choice and multi-select rendering.
  3. Gate questions ("I am ready to continue", "Done", etc.) render as a plain
     Continue button with no answer-checking.
  4. Free-text and MC pages auto-append a bottom-out hint that reveals the answer
     after all authored hints are exhausted.
  5. Multi-select questions (detected from question text + multiple answers, or from
     Options column with multiple correct answers) render as checkboxes requiring
     ALL correct answers to be selected, with no extras.
  6. dict key uses a tuple (curriculum, problem_set) instead of a hyphen-joined
     string, so IDs that happen to contain hyphens never corrupt the split.
  7. Output goes to 'IES-DLP-generated-webpages/' by default.
"""

import json
import os
import random
import re
import string
import sys

import pandas as pd


# ── detection ───────────────────────────────────────────────────────────────

READY_PHRASES = {
    "i am ready to continue",
    "i am finished with this assignment",
    "i have completed the assignment",
    "i am ready to proceed",
    "i have loaded the data and am ready for part 1",
    "i have completed",
    "done",
    "i am finished",
    "i am ready",
    "only continue once you have tried this on your own",
    "i am ready to proceed.",
}

MULTISELECT_RE = re.compile(
    r"select all that apply"
    r"|check all that apply"
    r"|check all statements"
    r"|more than one answer may be correct"
    r"|please select all"
    r"|select.*all.*true",
    re.IGNORECASE,
)


def is_ready_gate(answers: list) -> bool:
    """Single-answer gate questions like 'I am ready to continue'."""
    return len(answers) == 1 and answers[0].strip().lower() in READY_PHRASES


def is_multiselect(question: str) -> bool:
    """Detect 'select all that apply' phrasing in the question text."""
    return bool(MULTISELECT_RE.search(question))


# ── file naming ─────────────────────────────────────────────────────────────

def _rand(n: int = 4) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def generate_filename(curriculum: str, problem_set: str, question_number) -> str:
    """
    Use the full problem_set code (not just first 3 chars) so each question gets a
    unique, human-readable filename.
    e.g. CPSA-PRABU5RA-Q1-xK3z.html  (not CPSA-PSPRA-PSPRAQ1-xK3z.html)
    """
    c = "C" + curriculum[:3].upper()
    ps = problem_set.upper()
    return f"{c}-{ps}-Q{question_number}-{_rand(4)}.html"


def generate_end_filename(curriculum: str, problem_set: str) -> str:
    c = "C" + curriculum[:3].upper()
    ps = problem_set.upper()
    return f"{c}-{ps}-QZ-END-{_rand(7)}.html"


# ── shared CSS ──────────────────────────────────────────────────────────────

_CSS = """
body {
    font-family: Arial, sans-serif;
    background-color: #f4f6f9;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    margin: 0;
    padding: 28px 16px;
    box-sizing: border-box;
}
.container {
    background: #fff;
    border-radius: 12px;
    padding: 40px 44px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    max-width: 740px;
    width: 100%;
}
.header {
    font-size: 12px;
    font-weight: 700;
    color: #999;
    letter-spacing: .07em;
    text-transform: uppercase;
    margin-bottom: 18px;
}
.question {
    font-size: 16px;
    line-height: 1.75;
    color: #1a1a1a;
    margin-bottom: 28px;
}
.note {
    font-size: 13px;
    color: #888;
    font-style: italic;
    margin-top: 4px;
}
.btn {
    background: #0066ff;
    color: #fff;
    border: none;
    padding: 9px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: background .15s;
}
.btn:hover  { background: #004ecc; }
.btn:disabled { background: #bbb; cursor: default; pointer-events: none; }
.btn-ghost {
    background: #f0f4ff;
    color: #0066ff;
    border: 1.5px solid #cce0ff;
}
.btn-ghost:hover { background: #ddeaff; }
.btn-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 22px;
    align-items: center;
}
#feedback {
    margin-top: 14px;
    font-size: 15px;
    font-weight: 700;
    min-height: 22px;
}
.correct   { color: #1b7a2a; }
.incorrect { color: #c0250a; }
#hintDisplay {
    display: none;
    margin-top: 14px;
    font-style: italic;
    color: #555;
    font-size: 14px;
    line-height: 1.6;
    background: #f7faff;
    border-left: 3px solid #99c2ff;
    padding: 10px 14px;
    border-radius: 0 5px 5px 0;
}
#nextButton { display: none; }
.option-label {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 5px 0;
    padding: 8px 10px;
    border-radius: 6px;
    border: 1.5px solid transparent;
    cursor: pointer;
    font-size: 15px;
    line-height: 1.5;
    transition: background .1s, border-color .1s;
}
.option-label:hover { background: #f0f6ff; border-color: #cce0ff; }
.option-label input { margin-top: 3px; flex-shrink: 0; }
.text-row {
    display: flex;
    align-items: center;
    gap: 12px;
}
#answer {
    flex: 1;
    border: none;
    border-bottom: 2px solid #ccc;
    padding: 8px 2px;
    font-size: 16px;
    outline: none;
    background: transparent;
    transition: border-color .15s;
}
#answer:focus { border-bottom-color: #0066ff; }
"""


# ── HTML shell ──────────────────────────────────────────────────────────────

def _page(title: str, body: str) -> str:
    return (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '  <meta charset="UTF-8">\n'
        f'  <title>{title}</title>\n'
        f'  <style>{_CSS}</style>\n'
        '</head>\n'
        '<body>\n'
        f'{body}\n'
        '</body>\n'
        '</html>'
    )


# ── page templates ──────────────────────────────────────────────────────────

def create_end_page(curriculum: str, problem_set: str) -> str:
    code = _rand(7)
    body = (
        '<div class="container" style="text-align:center;margin-top:60px;">\n'
        '  <p style="font-size:13px;font-weight:700;color:#aaa;letter-spacing:.07em;'
        'text-transform:uppercase;">Assignment Complete</p>\n'
        '  <p style="font-size:16px;color:#555;margin-top:8px;">Your completion code:</p>\n'
        f'  <p style="font-size:36px;font-weight:800;letter-spacing:.12em;'
        f'color:#0066ff;margin:16px 0;">{code}</p>\n'
        '</div>'
    )
    return _page(f"{curriculum} – {problem_set} – Complete", body)


def create_continue_page(header: str, formatted_q: str, next_page: str) -> str:
    """Progress-gate: no answer input, just a Continue button."""
    body = (
        '<div class="container">\n'
        f'  <div class="header">{header}</div>\n'
        f'  <div class="question">{formatted_q}</div>\n'
        '  <div class="btn-row">\n'
        f'    <a class="btn" href="{next_page}">Continue &rarr;</a>\n'
        '  </div>\n'
        '</div>'
    )
    return _page(header, body)


def create_text_page(header: str, formatted_q: str, answers: list, hints: list, next_page: str) -> str:
    """Free-text input. Appends a bottom-out hint that reveals the correct answer."""
    all_hints = hints + (["The answer is: " + str(answers[0])] if answers else [])
    hints_js = json.dumps(all_hints)
    correct_js = json.dumps([str(a) for a in answers])

    body = f"""<div class="container">
  <div class="header">{header}</div>
  <div class="question">{formatted_q}</div>
  <div class="text-row">
    <input type="text" id="answer" placeholder="Your answer" autocomplete="off">
    <button class="btn" id="submitBtn" onclick="checkAnswer()">Submit</button>
  </div>
  <div id="feedback"></div>
  <div id="hintDisplay"></div>
  <div class="btn-row">
    <button class="btn btn-ghost" id="hintBtn" onclick="showHint()">Show Hint</button>
    <a class="btn" id="nextButton" href="{next_page}">Next &rarr;</a>
  </div>
</div>
<script>
  var hints = {hints_js};
  var hintIndex = 0;
  var correctAnswers = {correct_js};

  document.getElementById('answer').addEventListener('keypress', function(e) {{
    if (e.key === 'Enter') {{ e.preventDefault(); checkAnswer(); }}
  }});

  function showHint() {{
    var d = document.getElementById('hintDisplay');
    d.style.display = 'block';
    d.textContent = hintIndex < hints.length ? hints[hintIndex++] : 'No more hints.';
  }}

  function checkAnswer() {{
    var ans = document.getElementById('answer').value.trim();
    if (!ans) return;
    var fb = document.getElementById('feedback');
    if (correctAnswers.map(function(a) {{ return a.toLowerCase(); }}).indexOf(ans.toLowerCase()) !== -1) {{
      fb.innerHTML = '&#10003; Correct!';
      fb.className = 'feedback correct';
      document.getElementById('answer').disabled = true;
      document.getElementById('submitBtn').disabled = true;
      document.getElementById('hintBtn').style.display = 'none';
      document.getElementById('hintDisplay').style.display = 'none';
      document.getElementById('nextButton').style.display = 'inline-block';
    }} else {{
      fb.innerHTML = '&#10007; Incorrect — try again.';
      fb.className = 'feedback incorrect';
    }}
  }}
</script>"""
    return _page(header, body)


def create_mc_page(header: str, formatted_q: str, answers: list, options: list,
                   hints: list, next_page: str) -> str:
    """Radio-button multiple choice. Options column required for this template."""
    all_hints = hints + (["The answer is: " + str(answers[0])] if answers else [])
    hints_js = json.dumps(all_hints)
    correct_js = json.dumps([str(a) for a in answers])

    opts_html = "\n".join(
        f'    <label class="option-label">'
        f'<input type="radio" name="mc_choice" value="{opt}"> {opt}</label>'
        for opt in options
    )

    body = f"""<div class="container">
  <div class="header">{header}</div>
  <div class="question">{formatted_q}</div>
  <div id="options">
{opts_html}
  </div>
  <div id="feedback"></div>
  <div id="hintDisplay"></div>
  <div class="btn-row">
    <button class="btn" id="submitBtn" onclick="checkAnswer()">Submit</button>
    <button class="btn btn-ghost" id="hintBtn" onclick="showHint()">Show Hint</button>
    <a class="btn" id="nextButton" href="{next_page}">Next &rarr;</a>
  </div>
</div>
<script>
  var hints = {hints_js};
  var hintIndex = 0;
  var correctAnswers = {correct_js};

  function showHint() {{
    var d = document.getElementById('hintDisplay');
    d.style.display = 'block';
    d.textContent = hintIndex < hints.length ? hints[hintIndex++] : 'No more hints.';
  }}

  function checkAnswer() {{
    var sel = document.querySelector('input[name="mc_choice"]:checked');
    var fb = document.getElementById('feedback');
    if (!sel) {{
      fb.textContent = 'Please select an answer.';
      fb.className = 'feedback incorrect';
      return;
    }}
    if (correctAnswers.map(function(a) {{ return a.toLowerCase(); }}).indexOf(sel.value.trim().toLowerCase()) !== -1) {{
      fb.innerHTML = '&#10003; Correct!';
      fb.className = 'feedback correct';
      document.getElementById('submitBtn').disabled = true;
      document.querySelectorAll('input[name="mc_choice"]').forEach(function(r) {{ r.disabled = true; }});
      document.getElementById('hintBtn').style.display = 'none';
      document.getElementById('hintDisplay').style.display = 'none';
      document.getElementById('nextButton').style.display = 'inline-block';
    }} else {{
      fb.innerHTML = '&#10007; Incorrect — try again.';
      fb.className = 'feedback incorrect';
    }}
  }}
</script>"""
    return _page(header, body)


def create_multiselect_page(header: str, formatted_q: str, answers: list, options: list,
                             hints: list, next_page: str) -> str:
    """
    Checkbox multi-select. Student must select ALL correct answers and no extras.

    `options` = full displayed choice list (correct + distractors from Options column).
    `answers` = the correct subset.

    When no Options column is provided, options == answers, making the question
    trivially easy since only correct answers are shown. The CSV should be updated
    with a full distractor set in the Options column to fix this.
    """
    all_hints = hints + (["The correct answers are: " + "; ".join(str(a) for a in answers)] if answers else [])
    hints_js = json.dumps(all_hints)
    correct_js = json.dumps([str(a) for a in answers])   # original case; lowercased at comparison time in JS
    display_options = options if options else answers

    opts_html = "\n".join(
        f'    <label class="option-label">'
        f'<input type="checkbox" class="ms_check" value="{opt}"> {opt}</label>'
        for opt in display_options
    )

    note = ""
    if not options:
        note = (
            '\n  <p class="note">'
            '(Add an Options column to the CSV with all choices including distractors '
            'to make this question non-trivial.)</p>'
        )

    body = f"""<div class="container">
  <div class="header">{header}</div>
  <div class="question">{formatted_q}
    <div class="note">Select all that apply.</div>
  </div>{note}
  <div id="options">
{opts_html}
  </div>
  <div id="feedback"></div>
  <div id="hintDisplay"></div>
  <div class="btn-row">
    <button class="btn" id="submitBtn" onclick="checkAnswer()">Submit</button>
    <button class="btn btn-ghost" id="hintBtn" onclick="showHint()">Show Hint</button>
    <a class="btn" id="nextButton" href="{next_page}">Next &rarr;</a>
  </div>
</div>
<script>
  var hints = {hints_js};
  var hintIndex = 0;
  var correctAnswers = {correct_js};

  function showHint() {{
    var d = document.getElementById('hintDisplay');
    d.style.display = 'block';
    d.textContent = hintIndex < hints.length ? hints[hintIndex++] : 'No more hints.';
  }}

  function checkAnswer() {{
    var checked = Array.from(document.querySelectorAll('.ms_check:checked'))
                       .map(function(cb) {{ return cb.value.trim().toLowerCase(); }});
    var fb = document.getElementById('feedback');
    if (checked.length === 0) {{
      fb.textContent = 'Please select at least one answer.';
      fb.className = 'feedback incorrect';
      return;
    }}
    // Lowercase at comparison time — correctAnswers stores original case from the CSV
    var correctLower = correctAnswers.map(function(a) {{ return a.toLowerCase(); }});
    var allCorrect = correctLower.every(function(a) {{ return checked.indexOf(a) !== -1; }});
    var noExtras   = checked.every(function(a) {{ return correctLower.indexOf(a) !== -1; }});
    if (allCorrect && noExtras) {{
      fb.innerHTML = '&#10003; Correct!';
      fb.className = 'feedback correct';
      document.getElementById('submitBtn').disabled = true;
      document.querySelectorAll('.ms_check').forEach(function(cb) {{ cb.disabled = true; }});
      document.getElementById('hintBtn').style.display = 'none';
      document.getElementById('hintDisplay').style.display = 'none';
      document.getElementById('nextButton').style.display = 'inline-block';
    }} else if (!allCorrect) {{
      fb.innerHTML = '&#10007; Not all correct answers are selected.';
      fb.className = 'feedback incorrect';
    }} else {{
      fb.innerHTML = '&#10007; One or more selected answers is incorrect.';
      fb.className = 'feedback incorrect';
    }}
  }}
</script>"""
    return _page(header, body)


# ── router ──────────────────────────────────────────────────────────────────

def create_html_content(curriculum: str, problem_set: str, question_number: int,
                        question: str, answers: list, options: list,
                        hints: list, next_page: str) -> str:
    header = f"{curriculum} – {problem_set} – Q{question_number}"
    formatted_q = question.replace("\n", "<br>")

    # 1. Progress gate — no answer input needed
    if is_ready_gate(answers):
        return create_continue_page(header, formatted_q, next_page)

    # 2. Options column populated — choose MC or multi-select
    if options:
        if is_multiselect(question) or len(answers) > 1:
            return create_multiselect_page(header, formatted_q, answers, options, hints, next_page)
        return create_mc_page(header, formatted_q, answers, options, hints, next_page)

    # 3. No Options column but question text signals multi-select with multiple answers
    if is_multiselect(question) and len(answers) > 1:
        return create_multiselect_page(header, formatted_q, answers, [], hints, next_page)

    # 4. Default: free-text input
    return create_text_page(header, formatted_q, answers, hints, next_page)


# ── CSV → webpages ──────────────────────────────────────────────────────────

def generate_webpages_from_csv(csv_file: str,
                               output_folder: str = "IES-DLP-generated-webpages") -> None:
    """
    Read a CSV with columns: Curriculum, Problem Set, Question, Answer, [Options,] Hint
    and write one HTML file per question plus one end page per problem set.

    The optional Options column holds pipe-separated answer choices, e.g.:
        Sigmoid|Softmax|ReLU|tanh|Linear

    When Options is populated the question renders as radio buttons (single answer)
    or checkboxes (multi-select). When absent it falls back to a free-text input.
    """
    os.makedirs(output_folder, exist_ok=True)
    df = pd.read_csv(csv_file)
    has_options_col = "Options" in df.columns

    current_curriculum: str | None = None
    current_problem_set: str | None = None

    # key: (curriculum, problem_set) tuple — avoids hyphen-split fragility
    questions_per_ps: dict[tuple, list] = {}
    end_filenames:    dict[tuple, str]  = {}

    for _, row in df.iterrows():
        if pd.notna(row.get("Curriculum")):
            current_curriculum = str(row["Curriculum"]).strip()
        if pd.notna(row.get("Problem Set")):
            current_problem_set = str(row["Problem Set"]).strip()
        if not current_curriculum or not current_problem_set:
            continue

        key = (current_curriculum, current_problem_set)
        qs = questions_per_ps.setdefault(key, [])

        # New question row
        if pd.notna(row.get("Question")):
            q_num = len(qs) + 1
            fname = generate_filename(current_curriculum, current_problem_set, q_num)
            q_dict: dict = {
                "curriculum":   current_curriculum,
                "problem_set":  current_problem_set,
                "question":     str(row["Question"]).strip(),
                "answers":      [],
                "options":      [],
                "hints":        [],
                "filename":     fname,
            }
            # Parse options from this row if present
            if has_options_col and pd.notna(row.get("Options")):
                raw = str(row["Options"]).strip()
                if raw:
                    q_dict["options"] = [o.strip() for o in raw.split("|") if o.strip()]
            qs.append(q_dict)

        if not qs:
            continue

        current_q = qs[-1]

        if pd.notna(row.get("Answer")):
            current_q["answers"].append(str(row["Answer"]).strip())
        if pd.notna(row.get("Hint")):
            current_q["hints"].append(str(row["Hint"]).strip())
        # Options on answer/hint continuation rows (only if not yet set)
        if has_options_col and not current_q["options"] and pd.notna(row.get("Options")):
            raw = str(row["Options"]).strip()
            if raw:
                current_q["options"] = [o.strip() for o in raw.split("|") if o.strip()]

    # Pre-generate end-page filenames so the last question can link to them
    for curriculum, problem_set in questions_per_ps:
        end_filenames[(curriculum, problem_set)] = generate_end_filename(curriculum, problem_set)

    # Write question pages
    q_total = 0
    for key, qs in questions_per_ps.items():
        curriculum, problem_set = key
        for i, qd in enumerate(qs):
            next_file = qs[i + 1]["filename"] if i < len(qs) - 1 else end_filenames[key]
            html = create_html_content(
                qd["curriculum"], qd["problem_set"], i + 1,
                qd["question"], qd["answers"], qd["options"], qd["hints"], next_file,
            )
            out_path = os.path.join(output_folder, qd["filename"])
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
        q_total += len(qs)

        # Write end page
        end_html = create_end_page(curriculum, problem_set)
        with open(os.path.join(output_folder, end_filenames[key]), "w", encoding="utf-8") as f:
            f.write(end_html)

    print(
        f"Generated {q_total} question page(s) and "
        f"{len(questions_per_ps)} end page(s) in '{output_folder}/'"
    )


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python WebpageGenerator3.py <path_to_csv> [output_folder]")
        sys.exit(1)
    _csv  = sys.argv[1]
    _out  = sys.argv[2] if len(sys.argv) > 2 else os.path.join("IES", "IES-DLP-generated-webpages")
    generate_webpages_from_csv(_csv, _out)
