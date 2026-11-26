"""Smoke test for the bundled scripts. Run from the repo root: python tools/selftest.py"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "study-buddy" / "scripts"


def run(*args, expect=0):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != expect:
        sys.exit(f"FAILED {' '.join(map(str, args))}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        idx, prog = tmp / "mock.index.json", tmp / "progress.json"
        run(S / "build_index.py", ROOT / "examples" / "sample-mock.md", "--out", idx, "--exam", "Sample")
        bank = json.loads(idx.read_text(encoding="utf-8"))
        assert bank["count"] == 4, bank["count"]
        assert bank["questions"][1]["answer"] == ["A", "C"] and bank["questions"][1]["select"] == 2
        shown = run(S / "question.py", idx, 1)
        assert "Answer" not in shown and "Quality gate" in shown
        assert run(S / "question.py", idx, 3, "--voice").startswith("Question 3 of 4.")
        run(S / "progress.py", "--progress", prog, "init", "--bank", idx, "--mode", "voice", "--score-every", "2")
        r1 = json.loads(run(S / "progress.py", "--progress", prog, "record", "--q", "1", "--answer", "B for ball"))
        assert r1["result"] == "correct", r1
        dup = json.loads(run(S / "progress.py", "--progress", prog, "record", "--q", "1", "--answer", "C"))
        assert dup.get("duplicate"), dup
        run(S / "progress.py", "--progress", prog, "next")
        r2 = json.loads(run(S / "progress.py", "--progress", prog, "record", "--q", "2", "--answer", "A and C"))
        assert r2["result"] == "correct" and r2["speak_score"], r2
        code = run(S / "progress.py", "--progress", prog, "resume-code")
        assert code.startswith("RESUME|Sample|"), code
        run(S / "build_index.py", "--check", idx)
        bp = ROOT / "study-buddy" / "assets" / "blueprint.example.json"
        run(S / "charts.py", bp, "--out", tmp)
        assert (tmp / "weights-donut.svg").exists()
    print("selftest OK")


if __name__ == "__main__":
    main()
