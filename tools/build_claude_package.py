"""Sync the Claude edition from the canonical skill and rebuild the upload ZIP.

The canonical skill lives in study-buddy/. The Claude edition (claude/study-buddy/)
is the same folder without Codex-only files, and claude/study-buddy.zip is what you
upload in Claude (Customize > Skills). Run after any change to study-buddy/:

    python tools/build_claude_package.py
"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "study-buddy"
DEST = ROOT / "claude" / "study-buddy"
ZIP = ROOT / "claude" / "study-buddy.zip"
SKIP_DIRS = {"agents", "__pycache__"}
SKIP_SUFFIXES = {".pyc"}


def wanted(path):
    rel = path.relative_to(SRC)
    return not (set(rel.parts) & SKIP_DIRS) and path.suffix not in SKIP_SUFFIXES


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    files = sorted(p for p in SRC.rglob("*") if p.is_file() and wanted(p))
    for p in files:
        target = DEST / p.relative_to(SRC)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, Path("study-buddy") / p.relative_to(SRC))
    print(f"synced {len(files)} files to {DEST.relative_to(ROOT)} and wrote {ZIP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
