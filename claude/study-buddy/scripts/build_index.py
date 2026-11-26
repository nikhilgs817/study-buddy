"""Build a Study Buddy question index from a mock exam or question bank.

Reads PDF, TXT, MD or VTT. Finds numbered questions ("Question 12", "Q12:", "12."),
options ("A." "B)" "(C)"), inline answers ("Answer: B", "Correct answer: A, D"),
explanations, and an answer-key section at the end ("Answer Key" / "Answers").
A separate key file can be passed with --key. Writes JSON that question.py and
progress.py read, then prints a validation report. Standard library only, with
optional pdfplumber / pypdf, or the pdftotext command, for PDFs.

Usage:
  python build_index.py mock.pdf --out study/<exam>/bank/mock.index.json [--key key.pdf] [--exam NAME]
  python build_index.py --check study/<exam>/bank/practice.index.json
Exit code 1 when the report has blocking problems (no questions, duplicates).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LETTERS = "ABCDEFGH"
WORDNUM = {"two": 2, "three": 3, "four": 4, "five": 5, "2": 2, "3": 3, "4": 4, "5": 5}

RE_Q_LABELLED = re.compile(r"^(?:question|ques\.?|q)\s*#?\s*(\d{1,4})\s*(?:of\s+\d+)?\s*[:.)\-]?\s*(.*)$", re.I)
RE_Q_NUMBERED = re.compile(r"^(\d{1,4})\s*[.)]\s+(\S.*)$")
RE_OPTION = re.compile(r"^(?:\(([A-Ha-h])\)|([A-H])\s*[.):]|([a-h])\))\s*(\S.*)$")
RE_ANSWER = re.compile(r"^(?:correct\s+answers?|answers?|correct\s+options?|key)\s*(?:is|are)?\s*[:\-=]\s*(.+)$", re.I)
RE_EXPLAIN = re.compile(r"^(?:explanation|rationale|reasoning|reference|references|why)\s*[:\-]\s*(.*)$", re.I)
RE_KEY_HEADING = re.compile(r"^(?:answer\s*key|answers(?:\s+and\s+explanations)?|answer\s*sheet|solutions)\s*:?\s*$", re.I)
RE_KEY_LINE = re.compile(r"^(?:q(?:uestion)?\s*)?(\d{1,4})\s*[.):\-]?\s*(?:answers?\s*[:\-]?\s*)?([A-H](?:\s*(?:,|&|/|and)\s*[A-H])*)\b\s*[.:\-]?\s*(.*)$", re.I)
RE_KEY_INLINE_PAIRS = re.compile(r"(\d{1,4})\s*[.):\-]\s*([A-H](?:\s*,\s*[A-H])*)\b")
RE_SELECT = re.compile(r"\b(?:choose|select|pick)\s+(two|three|four|five|[2-5])\b", re.I)
RE_EXHIBIT = re.compile(r"\b(exhibit|refer to the (?:diagram|image|figure|graphic|table)|shown (?:below|above))\b", re.I)
RE_PAGE_NOISE = re.compile(r"^(?:page\s*)?\d{1,4}\s*(?:/|of)\s*\d{1,4}$|^page\s+\d+$", re.I)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path):
    """Return a list of page texts, trying several extractors."""
    try:
        import pdfplumber  # noqa
        with pdfplumber.open(str(path)) as pdf:
            pages = [(p.extract_text() or "") for p in pdf.pages]
        if any(t.strip() for t in pages):
            return pages, "pdfplumber"
    except Exception:
        pass
    if shutil.which("pdftotext"):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.txt"
            subprocess.run(["pdftotext", "-layout", str(path), str(out)], check=False, capture_output=True)
            if out.exists():
                pages = out.read_text(encoding="utf-8", errors="replace").split("\f")
                if any(t.strip() for t in pages):
                    return pages, "pdftotext"
    try:
        import pypdf  # noqa
        reader = pypdf.PdfReader(str(path))
        pages = [(p.extract_text() or "") for p in reader.pages]
        if any(t.strip() for t in pages):
            return pages, "pypdf"
    except Exception:
        pass
    return [], "none"


def read_source(path):
    if path.suffix.lower() == ".pdf":
        return pdf_pages(path)
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.lower() == ".vtt":
        text = "\n".join(l for l in text.splitlines()
                         if l.strip() and "-->" not in l and l.strip() != "WEBVTT" and not l.strip().isdigit())
    return text.split("\f"), "text"


def clean(line):
    line = line.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("’", "'")
    return re.sub(r"[ \t]+", " ", line).strip()


def letters_of(text):
    text = text.upper()
    head = re.split(r"[.;]|\s(?:BECAUSE|EXPLANATION)\b", text, maxsplit=1)[0]
    found = re.findall(r"\b([A-H])\b", head)
    return sorted(set(found))


def lines_with_pages(pages):
    out = []
    for i, page in enumerate(pages, start=1):
        for raw in page.splitlines():
            line = clean(raw)
            if line and not RE_PAGE_NOISE.match(line):
                out.append((i, line))
    return out


def parse_key_lines(lines):
    key, expl = {}, {}
    current = None
    for _, line in lines:
        pairs = RE_KEY_INLINE_PAIRS.findall(line)
        if len(pairs) >= 2 and not RE_OPTION.match(line):
            for n, l in pairs:
                key[int(n)] = letters_of(l)
            current = None
            continue
        m = RE_KEY_LINE.match(line)
        if m:
            current = int(m.group(1))
            key[current] = letters_of(m.group(2))
            if m.group(3).strip():
                expl[current] = m.group(3).strip()
            continue
        e = RE_EXPLAIN.match(line)
        if current is not None:
            add = e.group(1) if e else line
            if add:
                expl[current] = (expl.get(current, "") + " " + add).strip()
    return key, expl


def split_questions(lines):
    """Return (blocks, key_lines). Each block: (number, page, [lines])."""
    labelled = sum(1 for _, l in lines if RE_Q_LABELLED.match(l))
    pattern = RE_Q_LABELLED if labelled >= 3 else RE_Q_NUMBERED
    blocks, key_lines = [], []
    current, last = None, 0
    in_key = False
    for page, line in lines:
        if in_key:
            key_lines.append((page, line))
            continue
        if blocks or current:
            if RE_KEY_HEADING.match(line):
                in_key = True
                if current:
                    blocks.append(current)
                    current = None
                continue
        m = pattern.match(line)
        if m and not RE_OPTION.match(line):
            n = int(m.group(1))
            sequential = (pattern is RE_Q_LABELLED and n > last) or n == last + 1 or (last == 0)
            if sequential:
                if current:
                    blocks.append(current)
                current = (n, page, [m.group(2)] if m.group(2) else [])
                last = n
                continue
        if current:
            current[2].append(line)
    if current:
        blocks.append(current)
    return blocks, key_lines


def parse_block(number, page, body):
    stem, options, answer, explanation = [], [], None, []
    mode = "stem"
    for line in body:
        a = RE_ANSWER.match(line)
        if a and letters_of(a.group(1)):
            answer = letters_of(a.group(1))
            mode = "explain"
            continue
        e = RE_EXPLAIN.match(line)
        if e:
            mode = "explain"
            if e.group(1):
                explanation.append(e.group(1))
            continue
        if mode == "explain":
            explanation.append(line)
            continue
        o = RE_OPTION.match(line)
        if o:
            letter = (o.group(1) or o.group(2) or o.group(3)).upper()
            expected = LETTERS[len(options)] if len(options) < len(LETTERS) else None
            if letter == expected:
                options.append({"letter": letter, "text": o.group(4).strip()})
                mode = "option"
                continue
        if mode == "option" and options:
            options[-1]["text"] += " " + line
        else:
            stem.append(line)
    stem_text = " ".join(stem).strip()
    m = RE_SELECT.search(stem_text)
    select = WORDNUM.get(m.group(1).lower(), 1) if m else 1
    return {
        "number": number,
        "page": page,
        "stem": stem_text,
        "options": options,
        "select": select,
        "type": "multi" if select > 1 else ("single" if options else "open"),
        "exhibit": bool(RE_EXHIBIT.search(stem_text)),
        "answer": answer,
        "explanation": " ".join(explanation).strip() or None,
        "domain": None,
    }


def display_text(q):
    parts = [q["stem"]]
    if q.get("select", 1) > 1 and not RE_SELECT.search(q["stem"]):
        parts.append(f"(Choose {q['select']}.)")
    for o in q.get("options", []):
        parts.append(f"{o['letter']}. {o['text']}")
    return "\n".join(p for p in parts if p)


def validate(index):
    qs = index.get("questions", [])
    problems, warnings = [], []
    nums = [q.get("number") for q in qs]
    if not qs:
        problems.append("no questions found")
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    if dupes:
        problems.append(f"duplicate numbers: {dupes}")
    if nums:
        missing = sorted(set(range(min(nums), max(nums) + 1)) - set(nums))
        if missing:
            warnings.append(f"missing numbers: {missing[:40]}{' ...' if len(missing) > 40 else ''}")
    for q in qs:
        n = q.get("number")
        opts = q.get("options") or []
        if q.get("type") != "open" and len(opts) < 2:
            warnings.append(f"Q{n}: fewer than two options - check page {q.get('page')}")
        if not q.get("answer"):
            warnings.append(f"Q{n}: no key")
        elif any(a not in [o["letter"] for o in opts] for a in q["answer"]) and opts:
            warnings.append(f"Q{n}: key {q['answer']} not among options")
        elif len(q["answer"]) != q.get("select", 1) and opts:
            warnings.append(f"Q{n}: key has {len(q['answer'])} letters but question asks for {q.get('select', 1)}")
        disp = q.get("question", "")
        if re.search(r"^(?:correct\s+)?answers?\s*[:\-]|^explanation\s*:", disp, re.I | re.M):
            problems.append(f"Q{n}: answer text inside the display field")
        if re.search(r"[✓✔]|\(correct\)", disp, re.I):
            warnings.append(f"Q{n}: display text may reveal the answer (tick or '(correct)')")
        if q.get("exhibit"):
            warnings.append(f"Q{n}: mentions an exhibit - render page {q.get('page')} and look at it")
    return problems, warnings


def report(index, problems, warnings):
    qs = index.get("questions", [])
    keyed = sum(1 for q in qs if q.get("answer"))
    multi = sum(1 for q in qs if q.get("select", 1) > 1)
    print(f"Questions: {len(qs)} | keyed: {keyed} | multi-select: {multi} | extractor: {index.get('source', {}).get('extractor', '-')}")
    for p in problems:
        print(f"PROBLEM  {p}")
    shown = warnings[:60]
    for w in shown:
        print(f"warning  {w}")
    if len(warnings) > len(shown):
        print(f"warning  ... {len(warnings) - len(shown)} more")
    if not problems and not warnings:
        print("OK")


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, nargs="?")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--key", type=Path, help="separate answer key file")
    ap.add_argument("--exam", default=None)
    ap.add_argument("--check", type=Path, help="validate an existing index and exit")
    args = ap.parse_args()

    if args.check:
        index = json.loads(args.check.read_text(encoding="utf-8-sig"))
        problems, warnings = validate(index)
        report(index, problems, warnings)
        sys.exit(1 if problems else 0)
    if not args.source or not args.source.exists():
        ap.error("source file not found")

    pages, extractor = read_source(args.source)
    if not any(p.strip() for p in pages):
        sys.exit("No text found. The PDF may be scanned: OCR it or ask for a text version.")
    lines = lines_with_pages(pages)
    blocks, key_lines = split_questions(lines)
    questions = [parse_block(n, p, body) for n, p, body in blocks]

    key, key_expl = parse_key_lines(key_lines) if key_lines else ({}, {})
    if args.key:
        kpages, _ = read_source(args.key)
        k2, e2 = parse_key_lines(lines_with_pages(kpages))
        key.update(k2)
        key_expl.update(e2)
    for q in questions:
        n = q["number"]
        if n in key and key[n]:
            if q["answer"] and q["answer"] != key[n]:
                q.setdefault("notes", []).append(f"inline answer {q['answer']} differs from key section {key[n]}; using key section")
            q["answer"] = key[n]
        if n in key_expl and not q["explanation"]:
            q["explanation"] = key_expl[n]
        if q["answer"] and len(q["answer"]) > 1 and q["select"] == 1:
            q["select"], q["type"] = len(q["answer"]), "multi"
        q["question"] = display_text(q)

    index = {
        "schema": "study-buddy.index/1",
        "exam": args.exam,
        "source": {"path": str(args.source), "name": args.source.name, "sha256": sha256(args.source),
                   "pages": len(pages), "extractor": extractor,
                   "key_path": str(args.key) if args.key else None},
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(questions),
        "questions": questions,
    }
    problems, warnings = validate(index)
    index["warnings"] = problems + warnings
    out = args.out or args.source.with_suffix(".index.json")
    atomic_write(out, index)
    print(f"Wrote {out}")
    report(index, problems, warnings)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
