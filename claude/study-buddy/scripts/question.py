"""Print exactly one learner-facing item from a Study Buddy bank index."""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("number", type=int)
    args = parser.parse_args()
    try:
        bank = json.loads(args.index.read_text(encoding="utf-8-sig"))
        rows = [row for row in bank["questions"] if row["number"] == args.number]
        if len(rows) != 1:
            parser.error("Question number is missing or duplicated. Check the source.")
        prompt = rows[0]["question"]
        if not isinstance(prompt, str) or not prompt.strip():
            parser.error("Question text is missing. Check the source.")
        if any(line.strip().lower().startswith(("answer:", "correct answer:", "explanation:"))
               for line in prompt.splitlines()):
            parser.error("The display field contains grading text. Repair the index first.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Question {args.number} of {len(bank['questions'])}")
    print(prompt)


if __name__ == "__main__":
    main()
