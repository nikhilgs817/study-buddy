"""Draw prep-pack charts from a blueprint.json as standalone SVG files.

Writes weights-donut.svg (domain weights with the question count in the middle)
and weights-bars.svg (horizontal bars with ~questions and weight status).
Standard library only.

Usage: python charts.py research/blueprint.json --out pack/
"""
import argparse
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

PALETTE = ["#2563eb", "#65a30d", "#7c3aed", "#ea580c", "#0891b2", "#db2777", "#ca8a04", "#475569"]
FONT = "Inter, 'Segoe UI', Arial, sans-serif"


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    domains = data.get("domains") or []
    if not domains:
        sys.exit("blueprint has no domains")
    total_w = sum(float(d.get("weight") or 0) for d in domains)
    if total_w <= 0:
        sys.exit("domain weights are missing or zero")
    if abs(total_w - 100) > 0.6:
        print(f"warning: weights total {total_w:g}, not 100", file=sys.stderr)
    for i, d in enumerate(domains):
        d.setdefault("color", PALETTE[i % len(PALETTE)])
    return data, domains, total_w


def donut(data, domains, total_w, size=300):
    cx = cy = size / 2
    r_out, r_in = size * 0.47, size * 0.29
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">']
    angle = -math.pi / 2
    for d in domains:
        frac = float(d["weight"]) / total_w
        a2 = angle + frac * 2 * math.pi
        large = 1 if frac > 0.5 else 0
        p = lambda r, a: (cx + r * math.cos(a), cy + r * math.sin(a))
        x1, y1 = p(r_out, angle); x2, y2 = p(r_out, a2)
        x3, y3 = p(r_in, a2); x4, y4 = p(r_in, angle)
        if frac >= 0.9999:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{(r_out + r_in) / 2}" fill="none" stroke="{d["color"]}" stroke-width="{r_out - r_in}"/>')
        else:
            parts.append(
                f'<path d="M{x1:.2f},{y1:.2f} A{r_out},{r_out} 0 {large} 1 {x2:.2f},{y2:.2f} '
                f'L{x3:.2f},{y3:.2f} A{r_in},{r_in} 0 {large} 0 {x4:.2f},{y4:.2f} Z" '
                f'fill="{d["color"]}" stroke="#fff" stroke-width="2"/>')
        mid = (angle + a2) / 2
        lx, ly = p((r_out + r_in) / 2, mid)
        if frac >= 0.06:
            parts.append(f'<text x="{lx:.1f}" y="{ly + 5:.1f}" text-anchor="middle" font-family="{FONT}" '
                         f'font-size="{size * 0.055:.1f}" font-weight="800" fill="#fff">{float(d["weight"]):g}%</text>')
        angle = a2
    exam = data.get("exam", {})
    q, m = exam.get("questions"), exam.get("minutes")
    centre = f"{q} Qs" if q else escape(str(exam.get("code", "")))
    parts.append(f'<text x="{cx}" y="{cy + 2}" text-anchor="middle" font-family="{FONT}" font-size="{size * 0.085:.1f}" '
                 f'font-weight="800" fill="#0f172a">{centre}</text>')
    if m:
        parts.append(f'<text x="{cx}" y="{cy + size * 0.075:.1f}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="{size * 0.045:.1f}" fill="#64748b">{m} min</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def bars(data, domains, total_w, width=640):
    row_h, top = 34, 8
    height = top + row_h * len(domains) + 6
    label_w, bar_max = 230, width - 230 - 150
    q_total = (data.get("exam") or {}).get("questions")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    wmax = max(float(d["weight"]) for d in domains)
    for i, d in enumerate(domains):
        y = top + i * row_h
        w = float(d["weight"])
        bw = max(4, bar_max * w / wmax)
        approx = d.get("approx_questions")
        if approx is None and q_total:
            approx = round(q_total * w / total_w)
        status = d.get("weight_status", "")
        name = escape(f'{d.get("id", "")} {d.get("name", "")}'.strip())
        parts.append(f'<text x="{label_w - 8}" y="{y + 18}" text-anchor="end" font-family="{FONT}" font-size="12" '
                     f'font-weight="700" fill="#0f172a">{name}</text>')
        parts.append(f'<rect x="{label_w}" y="{y + 6}" width="{bw:.1f}" height="16" rx="4" fill="{d["color"]}"/>')
        meta = f"{w:g}%" + (f" · ~{approx} Qs" if approx is not None else "") + (f" · {status}" if status else "")
        parts.append(f'<text x="{label_w + bw + 8:.1f}" y="{y + 18}" font-family="{FONT}" font-size="11" fill="#334155">{escape(meta)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("blueprint", type=Path)
    ap.add_argument("--out", type=Path, default=Path("."))
    args = ap.parse_args()
    data, domains, total_w = load(args.blueprint)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "weights-donut.svg").write_text(donut(data, domains, total_w), encoding="utf-8")
    (args.out / "weights-bars.svg").write_text(bars(data, domains, total_w), encoding="utf-8")
    print(f"wrote {args.out / 'weights-donut.svg'} and {args.out / 'weights-bars.svg'}")


if __name__ == "__main__":
    main()
