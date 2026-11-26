"""Keep Study Buddy mock-exam progress: grade attempts once, score, queues, resume code.

All commands take --progress PATH (the JSON file). Writes are atomic.

  init     --bank INDEX [--exam NAME] [--start N] [--end N] [--order sequential|random]
           [--mode text|voice|read-show|show-only] [--score-every 10]
  record   --q N --answer "B" | "A,D" | "3-1-2" [--confidence sure|guess] [--hinted] [--retry]
           Grades against the key. A second record for the same question is ignored
           (idempotent) unless --retry, which is stored separately.
  correct  --q N --answer X      learner corrects the answer they just gave (replaces the attempt)
  skip     --q N                 ungraded
  flag     --q N [--off]
  dispute  --q N --verdict stands|ambiguous|key-wrong|learner-right [--note TEXT] [--rescore LETTERS]
  next                           move the cursor to the next unanswered item in the queue
  status   [--json]              score line, by-domain table, missed/guessed/flagged
  queue    --kind missed|guessed|flagged|unanswered|disputed
  resume-code                    compact RESUME| line for chats without file storage
  prefs    [--mode M] [--score-every N]

Output is JSON for record/correct/dispute/next so the coach can act on it:
  {"result": "incorrect", "given": ["A"], "key": ["B"], "speak_score": false, "score": "Done 12 · Left 38 · 9/12 (75%)"}
"""
import argparse
import json
import os
import random
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

GRADED = ("correct", "incorrect")


def dumps(obj, **kw):
    return json.dumps(obj, ensure_ascii=False, **kw)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, data):
    path = Path(path)
    data["updated"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    check = load_json(path)
    if check.get("cursor") != data.get("cursor"):
        sys.exit("save verification failed")


def bank_of(prog):
    return {q["number"]: q for q in load_json(prog["bank"])["questions"]}


def norm(answer):
    """Turn a typed or spoken answer into sorted option letters (or an ordering string)."""
    a = answer.strip().upper()
    if re.search(r"\d\s*-\s*[\dA-H]", a):                 # ordering 3-1-2 or matching 1-C, 2-A
        return [p.replace(" ", "") for p in re.split(r"[,;]", a) if p.strip()]
    a = re.sub(r"\b([A-H])\s+(?:FOR|AS IN|LIKE)\s+[A-Z]+", r" \1 ", a)   # "B for ball"
    a = re.sub(r"\b(?:OPTION|OPTIONS|ANSWER|LETTER|AND|OR|THE|IS|MY|I|SAY|PICK|CHOOSE|GUESS|SURE)\b", " ", a)
    tokens = [t for t in re.split(r"[^A-Z]+", a) if t]
    letters = [t for t in tokens if len(t) == 1 and t in "ABCDEFGH"]
    if not letters and len(tokens) == 1 and len(tokens[0]) <= 5 and set(tokens[0]) <= set("ABCDEFGH"):
        letters = list(tokens[0])                          # "AD", "BCE"
    return sorted(set(letters))


def grade(given, key):
    if not key:
        return "unverified"
    return "correct" if sorted(given) == sorted(key) else "incorrect"


def totals(prog, bank=None):
    first = prog["attempts"]
    graded = [a for a in first.values() if a["result"] in GRADED]
    correct = sum(1 for a in graded if a["result"] == "correct")
    queue = prog["queue"]
    answered = {int(n) for n in first} | set(prog.get("skipped", []))
    left = sum(1 for n in queue if n not in answered)
    pct = round(100 * correct / len(graded)) if graded else 0
    return {"graded": len(graded), "correct": correct, "left": left, "done": len(first), "pct": pct,
            "line": f"Done {len(first)} · Left {left} · {correct}/{len(graded)} ({pct}%)"}


def by_domain(prog, bank):
    out = {}
    for n, a in prog["attempts"].items():
        if a["result"] not in GRADED:
            continue
        d = (bank.get(int(n)) or {}).get("domain") or "untagged"
        row = out.setdefault(d, {"graded": 0, "correct": 0})
        row["graded"] += 1
        row["correct"] += a["result"] == "correct"
    for row in out.values():
        row["pct"] = round(100 * row["correct"] / row["graded"])
    return out


def score_due(prog, t, end):
    every = int(prog["prefs"].get("score_every", 10))
    if end:
        return True
    return every > 0 and t["graded"] - prog.get("score_spoken_at", 0) >= every


def cmd_init(a):
    bank_path = Path(a.bank).resolve()
    bank = load_json(bank_path)
    nums = sorted(q["number"] for q in bank["questions"])
    start = a.start or nums[0]
    end = a.end or nums[-1]
    queue = [n for n in nums if start <= n <= end]
    if a.order == "random":
        random.shuffle(queue)
    if Path(a.progress).exists() and not a.force:
        sys.exit("progress file exists; use it (resume) or pass --force to start over")
    prog = {"schema": "study-buddy.progress/1", "exam": a.exam or bank.get("exam"),
            "bank": str(bank_path), "bank_sha256": (bank.get("source") or {}).get("sha256"),
            "created": now(), "prefs": {"mode": a.mode, "score_every": a.score_every, "order": a.order},
            "queue": queue, "cursor": {"current": queue[0] if queue else None, "phase": "asking"},
            "attempts": {}, "retries": [], "skipped": [], "flags": [], "disputes": {},
            "adjustments": [], "score_spoken_at": 0}
    save(a.progress, prog)
    print(dumps({"ok": True, "total": len(queue), "first": prog["cursor"]["current"], "mode": a.mode}))


def cmd_record(a, prog):
    bank = bank_of(prog)
    q = bank.get(a.q)
    if not q:
        sys.exit(f"Q{a.q} not in bank")
    given = norm(a.answer)
    if not given:
        sys.exit("could not read an answer; ask again")
    key = prog["disputes"].get(str(a.q), {}).get("effective_key") or q.get("answer") or []
    result = grade(given, key)
    entry = {"given": given, "key": q.get("answer"), "effective_key": key, "result": result,
             "confidence": a.confidence, "hinted": a.hinted, "at": now()}
    if a.retry:
        entry["q"] = a.q
        prog["retries"].append(entry)
        prog["cursor"] = {"current": a.q, "phase": "graded"}
        save(a.progress, prog)
        print(dumps({"result": result, "given": given, "key": key, "retry": True, "speak_score": False}))
        return
    if str(a.q) in prog["attempts"]:
        prev = prog["attempts"][str(a.q)]
        print(dumps({"duplicate": True, "result": prev["result"], "given": prev["given"],
                          "key": prev["effective_key"], "note": "already graded; nothing changed",
                          "speak_score": False}))
        return
    if len(given) != (q.get("select") or 1) and key and all(len(x) == 1 for x in given):
        print(dumps({"ask_again": True, "note": f"question asks for {q.get('select')} answers, got {len(given)}"}))
        return
    entry["domain"] = q.get("domain")
    prog["attempts"][str(a.q)] = entry
    if a.q in prog.get("skipped", []):
        prog["skipped"].remove(a.q)
    prog["cursor"] = {"current": a.q, "phase": "graded"}
    t = totals(prog)
    end = t["left"] == 0
    due = score_due(prog, t, end)
    if due:
        prog["score_spoken_at"] = t["graded"]
    save(a.progress, prog)
    detail = {}
    if len(key) > 1 or len(given) > 1:
        detail = {"right": sorted(set(given) & set(key)), "missed": sorted(set(key) - set(given)),
                  "extra": sorted(set(given) - set(key))}
    print(dumps({"result": result, "given": given, "key": key, **detail, "guess": a.confidence == "guess",
                      "speak_score": due, "finished": end, "score": t["line"]}))


def cmd_correct(a, prog):
    prev = prog["attempts"].get(str(a.q))
    if not prev:
        sys.exit(f"Q{a.q} has no attempt to correct")
    given = norm(a.answer)
    prev.update({"given": given, "result": grade(given, prev["effective_key"]), "corrected_at": now()})
    save(a.progress, prog)
    print(dumps({"result": prev["result"], "given": given, "key": prev["effective_key"], "score": totals(prog)["line"]}))


def cmd_skip(a, prog):
    if a.q not in prog["skipped"] and str(a.q) not in prog["attempts"]:
        prog["skipped"].append(a.q)
    save(a.progress, prog)
    print(dumps({"skipped": a.q, "score": totals(prog)["line"]}))


def cmd_flag(a, prog):
    flags = set(prog["flags"])
    flags.discard(a.q) if a.off else flags.add(a.q)
    prog["flags"] = sorted(flags)
    save(a.progress, prog)
    print(dumps({"flags": prog["flags"]}))


def cmd_dispute(a, prog):
    d = prog["disputes"].setdefault(str(a.q), {})
    d.update({"verdict": a.verdict, "note": a.note, "at": now()})
    if a.rescore:
        d["effective_key"] = norm(a.rescore)
        att = prog["attempts"].get(str(a.q))
        if att:
            before = att["result"]
            att["effective_key"] = d["effective_key"]
            att["result"] = grade(att["given"], d["effective_key"])
            if before != att["result"]:
                prog["adjustments"].append({"q": a.q, "from": before, "to": att["result"], "reason": a.verdict, "at": now()})
    save(a.progress, prog)
    print(dumps({"dispute": d, "score": totals(prog)["line"]}))


def cmd_next(a, prog):
    done = {int(n) for n in prog["attempts"]} | set(prog["skipped"])
    queue = prog["queue"]
    cur = prog["cursor"]["current"]
    idx = queue.index(cur) + 1 if cur in queue else 0
    nxt = next((n for n in queue[idx:] if n not in done), None)
    if nxt is None:
        nxt = next((n for n in queue if n not in done), None)
    prog["cursor"] = {"current": nxt, "phase": "asking" if nxt else "finished"}
    save(a.progress, prog)
    print(dumps({"next": nxt, "finished": nxt is None, "score": totals(prog)["line"]}))


def queue_of(prog, kind):
    att = prog["attempts"]
    if kind == "missed":
        return sorted(int(n) for n, x in att.items() if x["result"] == "incorrect")
    if kind == "guessed":
        return sorted(int(n) for n, x in att.items() if x.get("confidence") == "guess")
    if kind == "flagged":
        return sorted(prog["flags"])
    if kind == "disputed":
        return sorted(int(n) for n in prog["disputes"])
    done = {int(n) for n in att} | set(prog["skipped"])
    return [n for n in prog["queue"] if n not in done]


def cmd_status(a, prog):
    bank = bank_of(prog)
    t = totals(prog)
    doms = by_domain(prog, bank)
    info = {"exam": prog.get("exam"), "score": t["line"], "current": prog["cursor"],
            "by_domain": doms, "missed": queue_of(prog, "missed"), "guessed": queue_of(prog, "guessed"),
            "flagged": prog["flags"], "skipped": prog["skipped"], "disputed": queue_of(prog, "disputed"),
            "weak_domains": [d for d, r in sorted(doms.items(), key=lambda kv: kv[1]["pct"]) if r["graded"] >= 5][:3]}
    if a.json:
        print(dumps(info, indent=2))
        return
    print(f"{info['exam'] or ''}  {t['line']}")
    for d, r in sorted(doms.items(), key=lambda kv: kv[1]["pct"]):
        print(f"  {d:<32} {r['correct']}/{r['graded']} ({r['pct']}%)")
    for k in ("missed", "guessed", "flagged", "skipped", "disputed"):
        if info[k]:
            print(f"  {k}: {', '.join(map(str, info[k]))}")
    if info["weak_domains"]:
        print(f"  weakest (5+ attempts): {', '.join(info['weak_domains'])}")


def cmd_resume_code(a, prog):
    parts = []
    for n in sorted(prog["attempts"], key=int):
        x = prog["attempts"][n]
        g = "".join(x["given"])
        tag = g if x["result"] == "correct" else f"X({g}>{''.join(x['effective_key'] or []) or '?'})"
        parts.append(f"{n}{tag}{'~' if x.get('confidence') == 'guess' else ''}")
    nxt = prog["cursor"]["current"]
    code = (f"RESUME|{prog.get('exam') or ''}|bank:{Path(prog['bank']).name}|next:{nxt}|done:{','.join(parts)}"
            f"|flags:{','.join(map(str, prog['flags']))}|disputed:{','.join(prog['disputes'])}"
            f"|mode:{prog['prefs'].get('mode')}|score_every:{prog['prefs'].get('score_every')}")
    print(code)


def cmd_prefs(a, prog):
    if a.mode:
        prog["prefs"]["mode"] = a.mode
    if a.score_every is not None:
        prog["prefs"]["score_every"] = a.score_every
        prog["score_spoken_at"] = totals(prog)["graded"]
    save(a.progress, prog)
    print(dumps(prog["prefs"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--progress", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("--bank", required=True); p.add_argument("--exam")
    p.add_argument("--start", type=int); p.add_argument("--end", type=int)
    p.add_argument("--order", default="sequential", choices=["sequential", "random"])
    p.add_argument("--mode", default="text", choices=["text", "voice", "read-show", "show-only"])
    p.add_argument("--score-every", type=int, default=10); p.add_argument("--force", action="store_true")
    p = sub.add_parser("record"); p.add_argument("--q", type=int, required=True); p.add_argument("--answer", required=True)
    p.add_argument("--confidence", choices=["sure", "guess"]); p.add_argument("--hinted", action="store_true")
    p.add_argument("--retry", action="store_true")
    p = sub.add_parser("correct"); p.add_argument("--q", type=int, required=True); p.add_argument("--answer", required=True)
    p = sub.add_parser("skip"); p.add_argument("--q", type=int, required=True)
    p = sub.add_parser("flag"); p.add_argument("--q", type=int, required=True); p.add_argument("--off", action="store_true")
    p = sub.add_parser("dispute"); p.add_argument("--q", type=int, required=True)
    p.add_argument("--verdict", required=True, choices=["stands", "ambiguous", "key-wrong", "learner-right"])
    p.add_argument("--note", default=""); p.add_argument("--rescore")
    sub.add_parser("next")
    p = sub.add_parser("status"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("queue"); p.add_argument("--kind", required=True, choices=["missed", "guessed", "flagged", "unanswered", "disputed"])
    sub.add_parser("resume-code")
    p = sub.add_parser("prefs"); p.add_argument("--mode", choices=["text", "voice", "read-show", "show-only"])
    p.add_argument("--score-every", type=int)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    if a.cmd == "init":
        return cmd_init(a)
    if not Path(a.progress).exists():
        sys.exit("no progress file; run init first")
    prog = load_json(a.progress)
    if a.cmd == "queue":
        print(dumps(queue_of(prog, a.kind)))
        return
    {"record": cmd_record, "correct": cmd_correct, "skip": cmd_skip, "flag": cmd_flag, "dispute": cmd_dispute,
     "next": cmd_next, "status": cmd_status, "resume-code": cmd_resume_code, "prefs": cmd_prefs}[a.cmd](a, prog)


if __name__ == "__main__":
    main()
