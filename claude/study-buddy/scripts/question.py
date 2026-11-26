"""Print exactly one learner-facing item from a Study Buddy bank index.

Never prints the key or the explanation.

Usage:
  python question.py <index.json> N            on-screen form (stem + "A. ..." lines)
  python question.py <index.json> N --voice    speakable form ("Question 12 of 50. ... Option A, ...")
  python question.py <index.json> N --meta     also print type, select count, page, exhibit flag
"""
import argparse
import json
import re
import sys
from pathlib import Path

NUMWORDS = {2: "two", 3: "three", 4: "four", 5: "five"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("index", type=Path)
    parser.add_argument("number", type=int)
    parser.add_argument("--voice", action="store_true", help="speakable form for voice mode")
    parser.add_argument("--meta", action="store_true", help="print type, select count, page and exhibit flag")
    args = parser.parse_args()
    try:
        bank = json.loads(args.index.read_text(encoding="utf-8-sig"))
        rows = [row for row in bank["questions"] if row["number"] == args.number]
        if len(rows) != 1:
            parser.error("Question number is missing or duplicated. Check the source.")
        row = rows[0]
        prompt = row.get("question")
        if not isinstance(prompt, str) or not prompt.strip():
            parser.error("Question text is missing. Check the source.")
        if any(line.strip().lower().startswith(("answer:", "correct answer:", "explanation:"))
               for line in prompt.splitlines()):
            parser.error("The display field contains grading text. Repair the index first.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    total = len(bank["questions"])
    select = int(row.get("select") or 1)
    if args.voice and row.get("stem") and row.get("options"):
        stem = re.sub(r"\s+", " ", row["stem"]).strip()
        parts = [f"Question {args.number} of {total}.", stem if stem.endswith(("?", ".", ":")) else stem + "."]
        if select > 1 and not re.search(r"\b(choose|select|pick)\b", stem, re.I):
            parts.append(f"Choose {NUMWORDS.get(select, select)}.")
        for o in row["options"]:
            text = o["text"].strip()
            parts.append(f"Option {o['letter']}, {text}{'' if text.endswith(('.', '?', '!')) else '.'}")
        parts.append("Your answer?")
        print(" ".join(parts))
    else:
        kind = f"choose {select}" if select > 1 else {"open": "open answer"}.get(row.get("type"), "single choice")
        print(f"Question {args.number} of {total} · {kind}")
        print(prompt)
    if args.meta:
        print(f"[type={row.get('type')} select={select} page={row.get('page')} exhibit={bool(row.get('exhibit'))} "
              f"domain={row.get('domain')} keyed={bool(row.get('answer'))}]")


if __name__ == "__main__":
    main()
