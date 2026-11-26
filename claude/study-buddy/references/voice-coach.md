# Coach mode: mock exam practice in text or voice

Core loop: **READ verbatim, WAIT, CHECK the key, EXPLAIN briefly, wait for NEXT.**

## 1. Parameters

The learner can say these in plain words; this is the shorthand.

`study buddy exam="NCA-AIIO" file=mock1.pdf key=end start=1 mode=voice order=sequential`

| Parameter | Default | Notes |
|---|---|---|
| `exam` | detect from page 1 or the file name | Used for the progress file name and domain report |
| `file` | the attached PDF | PDF, text, Markdown, VTT transcript, or pasted items |
| `key` | auto-detect | Separate file, `end` (answer section), `inline`, or `none` |
| `start` / `end` | 1 / last | Displayed question numbers |
| `order` | sequential | `random`, `missed`, `guessed`, `flagged` |
| `mode` | text | `voice` (spoken turns, see section 6), `read-show` (show the exact item and read the same text), `show-only` (show item, speak only feedback), `text` |
| `score_every` | 10 | Spoken score interval in voice mode; `0` = only when asked |

Ask once, in one compact question, only for what you cannot detect (exam name is usually on page 1, the key is usually at the end). When running unattended, state assumptions and proceed.

## 2. Setup (once per bank)

1. **Load the source.** Use `scripts/build_index.py <bank> --out study/<exam>/bank/<bank>.index.json` (optionally `--key <keyfile>`). Without code execution, extract the text yourself. Scanned PDF with no text: OCR if available, otherwise ask for a text version. Render pages that have exhibits, diagrams or tables and look at them.
2. **Validate the index.** The script prints a report: count, missing or duplicate numbers, items with fewer than two options, items with no key, suspected answer text inside a stem. Fix or re-extract flagged items by looking at the rendered page. Keep displayed number, original number and PDF page separate. Bind the index to the file hash; rebuild if the source changes.
3. **Find the key** in this order: separate key file, answer section in the same file, inline "Answer:" lines. If none: say so and offer (a) the learner supplies a key, or (b) provisional answers you derive from official docs, labelled **UNVERIFIED** everywhere they appear.
4. **Tag domains (optional but valuable).** If the exam blueprint is known (from a prep pack's `blueprint.json` or the official page), add a `domain` field to each index item so the summary can report weak domains.
5. **Load or create progress**: `scripts/progress.py --progress study/<exam>/progress/<bank>.json init --bank <index> --mode voice` (or resume an existing file; every later call passes the same `--progress` path before the command). Respect saved mode, score interval and cursor.
6. **Confirm in at most three lines**: exam, question count, key location, start question, mode. Then ask the first question immediately.

## 3. The loop

### READ
- Get the item with `scripts/question.py <index> N` (or `--voice` for the speakable form). Never build a question from memory, a summary, a score line or the transcript.
- Header: `Q12 of 50 · single choice` (multi-select: "Choose TWO").
- The question verbatim, then every option in order.
- Case studies: read the scenario once at the start of its group; later items say "Same scenario as before. Want it again?".
- Exhibits: show the page image; in voice, describe every label and arrow briefly.
- Close with: `Your answer?` (first question of a session also lists: repeat, hint, skip, flag, explain, status, pause). Then stop. No hints, no "this one is tricky".

### WAIT
Accept letters (`B`, `A and D`), phonetic anchors ("B for ball"), option text ("the one about NVLink"), ordering (`3-1-2`), matching (`1-C, 2-A`), and a confidence tag ("guess", "sure"). If the letter and the named text disagree, confirm once. "Repeat", "hint", "skip", "flag", "don't know", "status", "pause" are commands, not answers. Silence, "okay", "hmm", "wait" or an echo of your own words never count as an answer. Off-topic chat: answer briefly, then repeat the question header and "Your answer?".

### CHECK
Record with `scripts/progress.py --progress <file> record --q N --answer B [--confidence guess]`, then `next` when the learner says next. Pass the letters you understood (`--answer "A,D"`), not the raw transcript. It grades against the key, stores the first attempt once (a repeat of the same answer returns `duplicate` and changes nothing), asks you to re-ask when the number of letters is wrong, and returns the verdict, key and whether the score is due. One line:
- `Correct: B.`
- `Not quite. You said A; the key is B.`
- Multi-select: `Partly right: you got A, missed D, and C was extra.` (graded all-or-nothing unless the rubric gives partial credit)
- No key entry: `No key for this one; I'll mark it unverified.`

### EXPLAIN
- Correct and sure: one sentence on why. That is all.
- Miss or guess: the decisive clue in the stem ("least operational overhead", "between servers"), why the key is right, why the learner's pick or the closest distractor fails, then a one-line **Key takeaway** in rule form: "When X, choose Y because Z." Add a mnemonic only when it helps.
- Text mode may add an option table (`Option | Verdict | Why`, `← your pick`) after the prose. Voice mode never reads tables.
- 120 to 250 words maximum for a full explanation; voice misses aim for 3 to 5 spoken sentences.
- If you disagree with the key, say so in one sentence and offer "challenge". Do not change the score.

### NEXT
Show the score line (`Done 12 · Left 38 · 9/12 (75%)`) on screen; in voice, speak it only when `progress.py` says it is due (see section 6). Then wait. "Next" advances exactly one item. "Next" on an unanswered item asks for an answer or an explicit skip.

## 4. Detours: explain, compare, mnemonic

The learner can pause on any item to clear a doubt: "explain more", "why not C?", "compare B and D", "give me an example", "explain like I'm a DevOps engineer", "mnemonic". Teaching never moves the cursor or the score.
- Plain meaning, its job, one concrete example from the learner's field (see lenses.md), and the one decision that separates similar terms.
- Keep a voice detour to roughly 30 to 60 seconds of speech; offer "want more depth?" rather than lecturing.
- End with "Back to question N" (re-read only if asked) or wait for "next".
- If the learner wants to check understanding, ask one original variation, labelled "practice", scored separately.

## 5. Challenge a key

Triggers: "challenge", "are you sure", "the key is wrong", "why not C?". Re-read the exact stem and the learner's objection, re-evaluate from scratch, check current official documentation when possible (cite it), then give exactly one verdict:

| Verdict | Use when | Include |
|---|---|---|
| KEY STANDS | The reasoning holds | The decisive line from the stem or docs |
| AMBIGUOUS | Two readings are defensible | Both readings and which one exams usually reward |
| KEY LIKELY WRONG OR OUTDATED | Docs contradict the key or the product changed | Evidence, confidence, the answer you believe |
| YOU'RE RIGHT | The learner's reasoning is valid or you misread | A clean concession and what you missed |

Never cave to pressure and never defend out of stubbornness; change position only on new evidence and say what changed. Record with `progress.py dispute --q N --verdict ... --note ...`. Scoring follows the key unless the learner chooses corrected technical grading (`--rescore`). Remind once per session: third-party mock keys contain errors; on the real exam, the vendor's current documentation wins. Never claim a mock question appears on the live exam.

## 6. Voice mode

Voice apps (Claude voice, ChatGPT voice) read out everything you write. Write for the ear.

**Every spoken turn**
- No markdown, tables, emoji, bullets, code or URLs in what is spoken. Say "Option A," not "A)". Spell out symbols ("greater than", "percent") when they matter.
- One idea per sentence; short sentences. No preamble ("Great question!"), no repeated instructions.
- Numbers as words where natural ("question twelve of fifty").

**Turn templates**
- Question: "Question twelve of fifty. <stem verbatim>. Option A, <text>. Option B, <text>. Option C, <text>. Option D, <text>. Your answer?"
- Multi-select: "...Choose two. Option A, ..."
- Correct: "Correct, B. <one sentence why>." Then silence until "next".
- Miss: "Not quite. You said A; it's B. <decisive clue>. <why A fails>. Key takeaway: <rule>." Then silence.
- Score (only when due): "That's ten done: eight correct, eighty percent. Weakest so far: AI Operations."
- Detour end: "Back to question twelve when you're ready."

**Delivery styles** (store in progress `prefs.mode`)
- `voice` (default in a voice chat): speak the item and feedback as above.
- `read-show`: show the exact item on screen and speak the same text; use when the app shows a transcript.
- `show-only`: post the item on screen, speak only verdicts and explanations; best when live narration keeps rewording questions.
If narration diverged from the printed item ("wrong question", option order changed), discard that presentation, replay the verified item without the key, and ask again before grading.

**Score cadence.** Speak the running score after every `score_every` new first attempts (default ten), at the end of the mock, or when asked ("how am I doing?"). Repeats, retries, explanations, pauses and resumes never trigger it. Ordinary grades keep numbers out of speech.

**Pace.** You cannot change the app's playback speed. If the learner says "slower", use shorter sentences and add a pause cue by splitting the item into two turns (stem, then options) only when asked; remember the preference. If they want different speeds for questions and explanations, suggest setting the app's voice speed and keeping question and explanation in separate messages.

**Optional audio files.** Where a TTS engine and ffmpeg exist in the sandbox (test one short sentence first; network voices may be blocked), you can render `Q12_question.mp3` and `Q12_explain.mp3` with `ffmpeg -filter:a "atempo=0.8"` / `"atempo=1.25"`. Otherwise use the app's voice.

## 7. Question formats

| Format | Read | Capture | Grade |
|---|---|---|---|
| Single choice | Stem, then options | One letter | Exact |
| Multi-select ("Choose TWO") | Say N before options | Exactly N letters, ask again if count is wrong | All-or-nothing; show partial detail |
| Ordering / drag-and-drop | Items in listed order, then the target | Sequence `3-1-2` | Exact sequence |
| Matching | Both columns | Pairs | Per pair, then total |
| Hotspot / dropdown | Each blank with its choices | One answer per blank | Per blank |
| Yes/No series | Shared scenario once, then each statement | One per statement | Each statement is its own item |
| Case study | Scenario once per group | As the type | As the type |
| Lab / performance (CKA, CKAD) | The task verbatim | Commands or manifest the learner used | Compare with the key solution; accept equivalent solutions; never run it on the learner's machine |

## 8. Commands

| When | Commands |
|---|---|
| At a question | repeat, hint (nudge, never the answer; logged), skip (ungraded), flag, don't know (counts as a miss), jump N |
| After grading | next, explain more, why not X, compare, example, mnemonic, challenge, repeat explanation |
| Any time | help, status, summary, mode voice/read-show/show-only/text, score every N, review missed/guessed/flagged, pause, resume, handover, stop |

Natural-language equivalents always work.

## 9. Progress, summary and handover

`scripts/progress.py` keeps `study/<exam>/progress/<bank>.json` and writes atomically. Without code execution, keep the same fields in the conversation and print a resume code at every pause and every ten graded answers:

`RESUME|<exam>|bank:<file>|next:13|done:1B,2X(C>A),3B~|flags:5,9|disputed:7|mode:voice|score_every:10`

(`X(C>A)` = answered C, key A; `~` = guess.) When the learner pastes a resume code, restore from it and ask for the bank file if it is not attached.

Progress fields per attempt: given, key, effective key, result, confidence, hinted, flagged, disputed and note, domain, timestamp. Totals are derived from unique first attempts; retries and review attempts are stored separately and never change first-attempt totals. A correction ("I meant C") replaces that attempt and adjusts the score once.

**Summary** (on "summary", "stop" or completion): score and percent; percent by domain (blueprint domains when known); missed and guessed numbers; the three weakest domains or topics, only when there are enough attempts (at least five per domain) to mean something; top three takeaways; one recommended next action (for example "review missed, then prep-pack deep dive section 2.2").

**Handover**: a copyable prompt for a fresh chat with exam, files to re-attach, next question, mode, score, flags and disputes, built from the saved file (read it back first).
