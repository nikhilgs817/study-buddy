# Visual style for study documents

The target look: light A4 pages that are colourful but calm, where every page has a picture, a table or a coloured box, and the eye can find the exam-relevant line in seconds. Build documents as HTML with `assets/study-pack.css`, then render with `scripts/render_pdf.py`. `assets/template.html` shows every component with sample content; open it before writing a pack.

## Page anatomy

1. **Hero (first page only):** dark navy to violet gradient, exam code + document name in large white type, one-line promise, format chips (questions and minutes, delivery, price and validity, pass mark or "pass mark not published").
2. **Section heading:** dark badge with the objective number (`1.2`), bold title, and a small right-aligned aside (which blueprint line it maps to, or how to use the section). Colour the badge with the domain colour (`badge d1`).
3. **Content block:** a diagram or table first, then two to four callouts. Prefer a 2x2 grid of callouts (`grid-2`) under the diagram.
4. **Footer:** `<EXAM> <document> · v1 · mapped to <vendor> blueprint · <date>` on the left (set per document in a `<style>@page { @bottom-left { content: "..." } }</style>` block) and `page / pages` on the right (automatic).

## Components (class names in study-pack.css)

| Component | Class | Use for |
|---|---|---|
| Hero and chips | `.hero`, `.chip`, `.chip.warn` | Cover |
| Section heading | `h2.sec` with `.badge.dN` and `.aside` | Every objective |
| Domain banner | `.domain-banner.dN` with `.w` weight | Start of each domain in the deep dive |
| Weights row | `.weights` (donut SVG + `.legend` + `.mnemo-box`) | "The exam on one screen" |
| Weight status pill | `.pill.official / .derived / .estimated` | Next to every weight |
| Callouts | `.callout.idea / .trap / .lens / .hook / .example / .note` with `.label` | THE IDEA, EXAM TRAP, LENS · FROM YOUR WORLD, MEMORY HOOK, WORKED EXAMPLE |
| Rosetta stone | `table.rosetta` | Exam vocabulary mapped to the learner's world |
| Flow diagram | `.lane.dN` > `.flow` > `.node` + `.arrow` | Pipelines, request paths, sequences |
| Stat cards | `.grid-3` > `.stat.dN` (`.big`, `.lbl`, `.small`) | Numbers to remember, worked results |
| Data table | `table.t` with `<thead>` | Comparisons, term tables |
| Bar ladder | `.ladder` > `.bar-row` | Ranked comparisons (precision, speed, cost) |
| Rapid recall | `table.t.recall` | Cover-and-answer drills |
| Self-check | `.card.selfcheck` and `.answers` | Deep-dive questions and answers |
| Practice item | `.q` with `.qh` and `ol` | Practice set |
| Sources box | `.sources` | Last block of every document |
| Dense mode | `<body class="dense">`, `.cols-2` | One to two page cheatsheet |

## Colour rules

- Domains keep one colour across all documents: D1 blue, D2 green, D3 violet, D4 orange, D5 cyan, D6 pink (CSS variables `--d1`...). Set the same colours in `blueprint.json` so charts match.
- Callout colours carry meaning and never change: idea blue, trap red, lens orange, hook green, example sky blue.
- Colour is never the only cue: every coloured box also has a label, every chart segment a printed percentage.

## Diagrams

Choose the drawing for the question it answers:
- "What happens when?" → a flow lane (left to right, initiating event first, response last).
- "Where does it sit?" → containment: boxes inside boxes (host, process, storage, network), drawn as nested `.card`s or an inline SVG.
- "Which is bigger/faster/costlier?" → bar ladder or stat cards.
- "How do these map?" → Rosetta stone or a two-column table.

Every arrow means one verb ("sends request", "loads model from", "runs on"); write it under the arrow (`.arrow small`) when it is not obvious. Keep node labels to two or three words with a small subtitle. For anything the CSS components cannot express (topologies, layered stacks), write a clean inline SVG: 9 to 11 pt labels, consistent left-to-right direction, generous spacing. See [triton-example.md](triton-example.md) for an architecture plus a sequence of the same system.

## Writing on the page

- Plain words first, the official term in bold, its acronym expanded once.
- One idea per callout, two to four sentences.
- Numbers with units and the arithmetic (`70B × 2 bytes = 140 GB`).
- Tables: five columns maximum; first column bold; cut words before shrinking type below 7.5 pt.
- Headings say what the reader learns ("Scaling GPU infrastructure for different use cases"), not "Section 2".

## Check before delivery

Render with `--png-preview` and look at every page image: no text clipped or overflowing a box, no table split leaving a lone row (use `.keep` or move the block), no orphaned heading at the bottom of a page, donut labels readable, footer present from page 2. Fix and re-render.
