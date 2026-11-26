# Study Buddy: Claude setup and usage

Study Buddy turns Claude into an exam coach. It does two main jobs:

1. **Voice mock coach.** Upload a mock exam or question bank PDF and practise one question at a time, by voice or text. It reads the question exactly as printed, waits for your answer, grades it against the key, explains briefly, and lets you stop to clear a doubt ("explain more", "why not C?") before moving on. It tracks your score and weak domains and can resume later.
2. **One-command prep pack.** Give it an exam name or code. It researches the official exam page and blueprint first, then public course outlines from Udemy, Coursera and other educators, works out the weight of each domain, and builds a full set of visual study documents: blueprint and study plan, cheatsheet, core guide, deep dive, mnemonics card and an original practice set you can be quizzed on straight away.

It also explains any topic on request, turns your course slides into a revision document, and reviews a mock you already finished.

---

## 1. Install

### Claude app (claude.ai, desktop or mobile)

1. Download [`claude/study-buddy.zip`](../claude/study-buddy.zip) from this repository.
2. In Claude, make sure **code execution and file creation** is turned on (it is needed for reading PDFs, keeping your score and making PDFs). For the prep pack, keep **web search** on too.
3. Open **Customize > Skills**, choose the upload option and select the ZIP. Enable **Study Buddy**. Menu names can differ slightly between app versions; see Anthropic's guide: [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
4. If an older Study Buddy is already installed, replace it with this one (or switch the old one off) so only one version answers.
5. Check it: start a new chat and type `Study Buddy, what can you do?`

### Claude Code

Copy the skill folder into your personal skills directory.

Windows PowerShell:

```powershell
git clone https://github.com/nikhilgs817/study-buddy.git
$dest = Join-Path $env:USERPROFILE '.claude\skills\study-buddy'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Recurse -Force -Path '.\study-buddy\claude\study-buddy\*' -Destination $dest
```

macOS or Linux:

```sh
git clone https://github.com/nikhilgs817/study-buddy.git
mkdir -p ~/.claude/skills/study-buddy
cp -R study-buddy/claude/study-buddy/. ~/.claude/skills/study-buddy/
```

The entry point must end up at `~/.claude/skills/study-buddy/SKILL.md`. Open Claude Code in the folder where you keep your study files and type `/study-buddy` or just ask "use Study Buddy ...".

Optional helpers (Claude Code on your own machine): Python 3.8 or newer for the bundled scripts; `pip install pdfplumber` for better PDF reading. For PDF output the renderer uses Chrome, Edge or Chromium if installed (Edge is on most Windows machines), otherwise WeasyPrint (`pip install weasyprint`). With none of them you still get HTML files you can print to PDF from your browser.

---

## 2. Practise a mock by voice

**Start in text, then talk.** Attaching files works best in a typed message.

1. New chat. Attach the mock exam PDF (and the answer key if it is a separate file).
2. Type:
   > Use Study Buddy. Index this mock and quiz me from question 1 in voice mode.
3. Claude confirms in up to three lines (exam, number of questions, where the key is, start question, mode) and asks question 1.
4. Switch the chat to voice and answer out loud.

**What to say**

| You say | What happens |
|---|---|
| "B" or "B for ball" | Graded. One-line verdict and a short reason |
| "A and D" | Multi-select answer |
| "C, guess" | Graded and logged as a guess, so it comes back in review |
| "Next" | The next question, read in full |
| "Repeat" | Reads the current question again |
| "Hint" | A nudge, never the answer (logged) |
| "Explain more" / "Why not C?" / "Compare B and D" | A short spoken explanation; your place is kept |
| "Give me a mnemonic" / "Explain it like a DevOps engineer" | Memory hook or an example from your world |
| "Challenge" / "I think the key is wrong" | Re-checks against official docs and gives one verdict: key stands, ambiguous, key likely wrong, or you're right |
| "Flag" / "Skip" | Mark for later / move on ungraded |
| "How am I doing?" | Score so far and weakest domain |
| "Score every five" / "Only show my score" | Changes how often the score is spoken (default every ten questions) |
| "Show only" | Questions appear on screen and only the feedback is spoken (use this if the voice keeps rewording questions) |
| "Wrong question" | Re-reads the exact printed question before grading |
| "Review my misses" / "Review guessed" / "Review flagged" | Drills just those questions |
| "Pause" / "Stop" | Saves progress and gives you a resume prompt |

**Tips**
- Voice mode reads everything out, so Study Buddy keeps spoken turns short and never reads tables or symbols aloud. Details stay in the chat transcript.
- If the app's voice cannot use the skill, keep the chat in text and use the app's **Read aloud** on each question.
- ChatGPT voice works the same way with the same skill where ChatGPT skills are available (see the README).

**Resume later.** On "pause", Claude saves `progress/<bank>.json` and shows a `RESUME|...` line. In a new claude.ai chat, attach the mock again plus the saved progress file (or paste the RESUME line) and say:
> Use Study Buddy. Resume my mock from this progress file in voice mode.

---

## 3. Build a prep pack with one command

> Study Buddy: prep pack for NCA-AIIO. Exam date 20 December. My background is DevOps (Jenkins, Ansible, Nexus, WebSphere).

Only the exam name or code is required. Exam date gives you a day-by-day plan (otherwise four weeks); background sets the examples (DevOps is built in). Attach your own course slides or notes and they are used too.

What happens, without further prompts:

1. **Research**: the official exam page and blueprint first, then official docs, then public course outlines (Udemy, Coursera, Pluralsight, KodeKloud, Whizlabs and others), then recent exam-experience posts for emphasis only. Every source is logged in `research/sources.md`.
2. **Weightage**: each domain's weight is marked **official**, **derived** (worked out from official numbers) or **estimated** (blended from objective counts, course time and practice-question topics, with the method stated). You also get approximate questions per domain.
3. **Documents** (HTML and PDF, A4):

| File | What it is |
|---|---|
| `00-<exam>-blueprint-and-plan` | Exam format, weight donut, domain table, study plan to your exam date |
| `01-<exam>-cheatsheet` | One or two dense pages for the night before |
| `02-<exam>-core-guide` | Visual guide: every objective with a diagram or table, THE IDEA, EXAM TRAP, DEVOPS LENS and MEMORY HOOK boxes, worked examples, rapid recall, exam-day tactics |
| `03-<exam>-deep-dive` | One section per official objective plus self-check questions with answers per domain |
| `04-<exam>-mnemonics` | Every memory hook on one page |
| `05-<exam>-practice-set` | Original exam-style questions in proportion to the weights, with a separate answer key; also saved as a bank so you can say "quiz me on the practice set" |

4. **Checks**: weights total 100, every official objective is covered, pages are rendered and looked at for clipped text or broken diagrams, and each document ends with a sources-and-confidence box.

Useful follow-ups: "Only make the cheatsheet", "Add Anki flashcards", "Make the deep dive for domain 2 longer", "Update my pack, the blueprint changed", "Quiz me on the practice set in voice mode".

Study Buddy only uses public pages: it does not copy paid course content or practice questions, and it never uses "brain dumps" of real exam questions. Practice questions it writes are original.

---

## 4. Where your files and progress live

| Where you use it | Files |
|---|---|
| claude.ai / desktop / mobile | Created in the chat's sandbox and offered as downloads. Download the PDFs and your progress JSON before you leave a long session; a new chat starts empty, so re-attach the mock and progress file to resume. In a Claude Project you can add them to project knowledge. |
| Claude Code | In your current folder, under `study/<exam>/` |

Layout inside `study/<exam>/`:

```
profile.json            your preferences: background, voice mode, score interval, exam date
sources/                your uploads (never edited)
bank/<bank>.index.json  the parsed question bank
progress/<bank>.json    attempts, score, flags, where you stopped
research/               blueprint.json, sources.md, coverage.md
pack/                   generated HTML + PDF documents
```

Keep personal study material in your own workspace, not in this repository.

---

## 5. Example prompts

| Goal | Prompt |
|---|---|
| Start a mock by voice | "Use Study Buddy. Quiz me from question 1 in voice mode." |
| Start mid-way | "Study Buddy, start at question 26 and stop at 50." |
| Random order | "Quiz me in random order, voice, score every five." |
| Review | "Review my misses and guesses, hide my old answers." |
| Explain a topic | "Explain NVLink vs InfiniBand with a DevOps example and a mnemonic." |
| Turn slides into notes | "Make a two-page visual cheat sheet from these slides with slide numbers and memory hooks." |
| Audit a bank | "Map this mock to the official objectives and list gaps and doubtful keys." |
| Full prep pack | "Prep pack for AWS SAA-C03, exam on 15 January, background DevOps." |

---

## 6. Troubleshooting

| Problem | Fix |
|---|---|
| Skill does not start | Say "Use Study Buddy" explicitly; check it is enabled in Customize > Skills |
| PDF has no text (scanned) | Ask for OCR, or upload a text or Word version |
| Questions or options look broken | Say "show me the index report"; Claude re-reads the page images and fixes the item |
| Voice reads tables or symbols | Say "voice mode" again, or "show only" |
| No PDF produced | You get HTML: open it in a browser, Print, Save as PDF, A4, "Background graphics" on |
| Score looks wrong | "Status" shows every graded item; "I meant C for question 12" corrects it once |

---

## 7. For maintainers

- Edit the canonical skill in `study-buddy/` (it also serves Codex via `agents/openai.yaml`).
- Run `python tools/selftest.py` to check the scripts.
- Run `python tools/build_claude_package.py` to refresh `claude/study-buddy/` and `claude/study-buddy.zip`, then commit both.
