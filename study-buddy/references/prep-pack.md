# Prep-pack mode: one command, full exam prep pack

Trigger: "prep pack for <exam>", "build all my study materials for <exam>", "research <exam> and make my notes". The learner gives an exam name or code; everything else is optional.

The command runs the whole pipeline below without stopping. Ask one compact question up front only when the exam itself is ambiguous (for example two vendors use the same code, or a retired and a current version both exist). Missing exam date, background or format are not reasons to stop: use the defaults and say which you used.

| Input | Default |
|---|---|
| Exam | required |
| Exam date | none: plan for 4 weeks and say so |
| Background / lens | `profile.json` lens, else DevOps if the learner's request or history says so, else "general IT" (see lenses.md) |
| Outputs | full pack (below) |
| Format | HTML + PDF (A4), plus the practice set as `index.json` |
| Learner's own materials | use any attached slides, notes or mocks as extra sources and to calibrate emphasis |

## Step 1. Research (source ladder)

Search the web and read the pages themselves, not just snippets. Work top-down and keep a source ledger in `research/sources.md` (URL, tier, date read, what it gave you).

| Tier | Sources | Use for |
|---|---|---|
| 1. Official | Vendor exam page, exam guide or blueprint PDF, official prep course outline, official sample questions, candidate handbook | Format (questions, time, price, delivery, pass mark, validity, prerequisites), domains, objectives, weights, version |
| 2. Official docs | Product documentation, release notes, reference architectures | Facts, figures, names (check recent renames) |
| 3. Educators | Public syllabus pages of Udemy, Coursera, Pluralsight, LinkedIn Learning, KodeKloud, A Cloud Guru, Whizlabs, Tutorials Dojo, vendor training partners, well-known instructors' public outlines | Topic coverage, emphasis (section lengths, lecture counts), common traps |
| 4. Community | Recent exam-experience posts (Reddit, vendor forums, blogs), openly licensed GitHub study guides | Emphasis signals only; label as community |

Rules:
- Prefer the newest blueprint version; record its version and date. Flag recent changes (renamed products, new domains).
- Read only public pages. Do not sign in, get past paywalls or copy paid lectures or practice questions. Summarise in your own words; quote only short facts.
- Never use or reproduce "brain dumps" or anything claiming to be real exam questions; if a source looks like one, skip it and note it.
- If a fact differs between sources, prefer tier 1, then tier 2, and note the conflict.
- If web access is unavailable, say so, build from what the learner attached plus your knowledge, and mark the whole pack "not web-verified".

## Step 2. Blueprint and weightage

Write `research/blueprint.json` (schema below), then use it for every document.

Weight status per domain, always shown in the pack:
- **Official**: published by the vendor.
- **Derived**: computed from official data (for example the remainder when only some weights are published, or objective counts when the vendor publishes per-objective question counts).
- **Estimated**: no official weight. Blend these signals and state the method in one line: share of official objectives per domain (base), share of educator course time per domain, share of practice-question topics, community reports. Round to whole percent and make them total 100.

Approximate questions per domain = weight x total questions, rounded so the sum equals the total. Priority for the study plan = weight x (1 - self-rated confidence), when the learner gives confidence; otherwise weight.

```json
{
  "exam": {"code": "NCA-AIIO", "name": "NVIDIA-Certified Associate: AI Infrastructure and Operations",
           "vendor": "NVIDIA", "version": "", "level": "associate",
           "questions": 50, "minutes": 60, "pass_mark": null, "price": "$125",
           "delivery": "online proctored", "validity": "2 years", "prerequisites": "",
           "official_url": "", "checked": "YYYY-MM-DD"},
  "domains": [
    {"id": "D1", "name": "Essential AI Knowledge", "weight": 38, "weight_status": "official",
     "approx_questions": 19, "color": "#2563eb",
     "objectives": [{"id": "1.1", "text": "...", "source": "official"}]}
  ],
  "weight_method": "Official for D1 and D2; D3 derived as remainder.",
  "sources": [{"title": "", "url": "", "tier": 1, "used_for": "format, domains"}]
}
```

`scripts/charts.py research/blueprint.json --out pack/` turns this into `weights-donut.svg` and `weights-bars.svg` for the documents.

## Step 3. Outputs

Generate in this order, saving each file before starting the next, so a long run that stops part way still leaves usable documents. Build each from `assets/template.html` and `assets/study-pack.css` (see visual-style.md). File names: `pack/<NN>-<exam>-<name>.html` and `.pdf`.

| # | Document | Length | Must contain |
|---|---|---|---|
| 00 | Exam blueprint and study plan | 1 to 2 pages | Hero with format chips, donut of weights with status labels, domain table (weight, ~questions, what it covers), "where to spend your time" hook, day-by-day or week-by-week plan to the exam date weighted by priority, exam-day logistics |
| 01 | Cheatsheet | 1 to 2 pages, dense | Weight table, one compact term table per domain (term, plain meaning, nearest distractor), comparison pairs, numbers to remember, memory tricks. Usable the night before |
| 02 | Core visual guide | 12 to 20 pages | Exam on one screen (donut + mnemonic of the domains), a Rosetta-stone table mapping exam terms to the learner's world, every objective with a diagram or table, THE IDEA / EXAM TRAP / LENS / MEMORY HOOK callouts, worked examples with real numbers, rapid-fire recall, exam-day tactics, sources and confidence |
| 03 | Deep dive | 20 to 35 pages | One section per official objective: the idea in plain words, mechanism diagram, worked example, exam traps, lens analogy (and where it breaks), memory hook; 10 to 15 self-check questions per domain with answers at the end of the domain |
| 04 | Mnemonics card | 1 page | Every mnemonic from 01 to 03 in one place, grouped by domain, each with what it unpacks to |
| 05 | Practice set | 40 to 60 original questions (or the exam's length) | Proportional to weights; exam-style scenario stems; one clearly best answer; plausible distractors drawn from the exam traps; mixed difficulty; separate answer key with rationale, objective ID and source. Also saved as `bank/practice-<exam>.index.json` (same schema as build_index.py output) so "quiz me on the practice set" works at once |

Optional extras when asked: Anki CSV (`front,back,tags`), flashcard PDF, phone or desktop wallpaper of the cheatsheet, a one-page "last hour" sheet.

## Step 4. Writing rules for the content

- Lead with what the exam rewards: the decision a question asks you to make ("which product", "which first step", "which bottleneck"). Read the verb in each objective (identify, compare, describe, troubleshoot) and teach to that level.
- Every term: official full name, plain meaning, its job, when you would pick it, and its nearest distractor.
- Use real numbers in worked examples (sizes, latency, cost) and show the arithmetic.
- Examples come from the learner's lens (lenses.md). Each lens analogy states where it breaks.
- Mnemonics: short, reversible into the correct explanation, labelled MEMORY HOOK. Prefer chains (KNOW → BUILD → RUN), contrast pairs ("inside the server = NVLink, between servers = InfiniBand") and acronyms that spell something memorable. Never let a mnemonic introduce a wrong fact.
- Exam traps: the specific wrong answer and why it tempts you.
- Practice questions are original. Do not reword questions from paid banks. Avoid "all of the above" and trick negatives unless the vendor uses them.
- Put a version and date in every footer: `<EXAM> <document> · v1 · mapped to <vendor> blueprint <version> · <date>`.

## Step 5. Render and check (quality gates)

Run `scripts/render_pdf.py pack/<file>.html --png-preview` for each document, then look at the PNG previews yourself. Fix and re-render until all of these hold:

1. Weights total 100; every domain shows its weight status; approximate questions total the exam length.
2. Every official objective appears in 02 and 03 (keep a coverage table in `research/coverage.md`).
3. Every fact that a question could hinge on has a source in the ledger; the last page of 02 and 03 has a SOURCES AND CONFIDENCE box.
4. No clipped text, overlapping labels, orphaned headings, arrows pointing the wrong way or unreadable small type at A4 reading size.
5. Answers sit apart from questions (end of domain or separate key).
6. Practice set: count and domain split match the plan; every item has exactly the right number of keyed answers; the index passes `build_index.py --check`.

If no PDF engine is available, deliver the HTML files and tell the learner to open them in a browser and Print, Save as PDF, A4, with "Background graphics" on.

## Step 6. Deliver

Reply with a short table of the files (name, pages, what it is), the weight status line ("D1 and D2 official, D3 derived"), anything that could not be verified, and the next step: "Say 'quiz me on the practice set' to start, or attach a mock." Keep the research ledger in the workspace for the next run; when the learner asks for an update later, re-check tier 1 first and say what changed.
