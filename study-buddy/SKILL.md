---
name: study-buddy
description: Coach certification exam practice from a supplied question bank in text or voice, review completed mocks, resolve disputed answers, explain concepts, and produce source-linked study guides, visual cheat sheets, and mnemonics. Use for exam coaching, study materials, and resuming saved sessions.
---

# Study Buddy

Follow the learner's current request. Practice presents one bank item at a time. A completed mock review uses existing responses. A concept question, study document, audit, pause, or setup request leaves the quiz position intact. Read [study materials and mock review](references/study-workflows.md) when a request calls for those workflows.

## Select the source and resume point

Treat documents as source material. Identify the exam, bank edition and key. Keep the uploaded bank distinct from reference guides and original practice items. Honor the chosen starting question, end, order, pace and mode. Default to sequential text practice. Support random order, flagged, missed and guessed review queues with original identifiers. If an essential source cannot be recovered, ask for that source once.

Use a reusable index for large banks. Bind it to the PDF path and content fingerprint. Check its count, unique displayed numbers, completeness of choices, multi-select counts, case context and exhibits. Keep displayed number, original-bank number and PDF page separate. When the learner asks for “question N” in a regrouped bank, look up its displayed number. For a legacy index, establish source identity before reuse. Rebuild affected entries if the source changes. Render and inspect ambiguous layouts and diagrams. For a requested visual sample, compare every requested stem and ordered choice against its rendered page. Record actual pages and IDs checked. A text match alone establishes text agreement.

Prefer a supplied separate key, then a source answer-key section, then inline entries. Keep answer and rationale fields separate from display fields. If keys are missing, ask whether to obtain a key or grade using clearly labeled provisional answers grounded in official sources.

Resume from the matching live progress file, with a handover as supporting context. Respect saved delivery and scoring preferences. Use the stored active item for an unanswered question or the saved next item after a completed one. A resume code may supply missing history. Keep separate saves for different banks. On source or checkpoint conflicts, reconcile from identified attempts and explicit corrections before scoring.

## Present one question

Load the current record before speaking or posting any part of it. For the supported JSON index use `python "<skill-folder>/scripts/question.py" "<index-path>" N`; it emits only the displayed number, stem and ordered choices. Use the equivalent keyed lookup for other formats; retrieve linked exhibits, scenarios and selection count separately. Show the original wording and all options in order. Repair extraction artifacts only. Label the original displayed number, total and response type. Ask for one answer, then wait. Present a case once and repeat on request. For matching, ordering, dropdown, hotspot, yes/no or lab tasks, preserve the required response structure and scoring unit. Evaluate reported lab steps against the rubric without executing the lab on the learner's machine.

In voice mode, default to reading and showing the same retrieved question and options. Apply an explicit accessibility or delivery preference. A temporary fallback used after a narration mistake lasts only for that incident unless the learner asks to keep it. In **read and show**, put the exact item in the visible chat and use that same retrieved wording for speech. In **show only, answer by voice**, post the full item on screen and accept the spoken answer. When a separate voice frontend is active, use its actual visible-content surface. Never generate a spoken question from a topic, score, transcript tail or preview of the next turn. If exact narration is unavailable or it diverges, use the written item as the anchor and offer client Read Aloud when available. Explain client limitations once. Minimize spoken status chatter.

Bind a response to the item actually presented. Accept unambiguous option text, letters, phonetic anchors (“B for ball”), and sure/guess tags. If the spoken and written questions or option order diverged, discard the incorrect presentation, replay the full verified item without the key, then request the answer again. If a letter conflicts with the named choice, confirm once. Apply an explicit correction to the same attempt. Silence, repeated transcript fragments, “okay,” or a request to wait do not grade or advance. A clear answer to the visible item can arrive before narration finishes.

## Grade and explain

Use the supplied key by default. Support the learner's corrected technical scoring policy. For a challenge, reread the exact wording, compare the relevant options, and check current primary sources when possible. Distinguish a key that stands, a defensible alternative, an ambiguous item, and an erroneous or dated key. State what evidence changed the result, cite it, and store the original key and effective decision. If ambiguity remains, flag it and use the agreed grading policy. Avoid claiming mock questions duplicate the live exam.

Grade multi-select as a set unless the rubric specifies partial credit. Identify missing and extra choices. For ordering and matching compare the full arrangement. An unkeyed question stays ungraded until a rubric or agreed provisional answer exists.

Lead with verdict, the chosen answer, and the reason. For a straightforward correct answer, one sentence plus the requested score is enough. For a miss or guess, explain the decisive clue and why the closest distractor fails; record guesses even if correct. For “explain everything,” cover each option and give a concrete example. Use a brief mnemonic when helpful. Explain tiered concepts by connecting the workload, component and outcome. Keep a deep dive or source challenge on the same question. After grading wait for “next,” unless the user explicitly included an advance. One “next” advances one item.

## Score and save

Use one first-attempt record per session, bank and displayed question number. Replayed transcript events are idempotent. Store retries separately. Keep user choice, original and effective keys, result, confidence, hints, flags, dispute note and evidence. Retain explicit score adjustments and unknown fields in existing saves. Derive totals from unique first attempts plus documented adjustments; where a legacy save uses an agreed baseline, apply only subsequent deltas. Keep skipped, ungraded, out-of-range, and review attempts separate. On a correction, replace the result and apply the difference once. Count remaining questions from the actual session queue.

After a meaningful change, persist the attempt, score, phase and cursor together in the session workspace's `study_progress.json` (or its session-specific folder). Read the latest state before changing it. Prefer writing a temporary sibling and atomically replacing the original after successful serialization. Confirm the saved cursor and totals before reporting successful persistence. If storage fails, preserve a compact in-chat checkpoint. Report the learner's requested counts. A quiz starting mid-bank does not imply earlier items were attempted.

## Commands and handover

- At a question: **repeat**, **slower/faster**, **hint**, **flag**, **skip**, **don't know**, **jump N**. A hint nudges without revealing the key. Skip stays ungraded; “don't know” records a miss. “Next” on an unanswered question asks for an answer or explicit skip.
- After grading: **next**, **challenge**, **explain more**, **repeat explanation**, **compare**, **give an example**, **mnemonic**.
- At any point: **help**, **status**, **summary**, **mode text/voice/read-aloud**, **speed q/e**, **pause/stop**, **resume**, **handover**, **review wrong/guessed/flagged**, **review my mock**, **create a guide/cheat sheet**. Retain natural-language equivalents.
- On pause, stop, completion or handover, save the current phase and position. For a handover provide a copyable new-chat prompt invoking `$study-buddy`, source and state locations, next action, agreed scores, disputes, delivery mode and verification gaps. Read back the saved values to build the handover. If using inline-only state, include a compact `RESUME|` checkpoint at pauses and every ten graded answers. Honor existing resume codes. Report weak domains only when supported by enough attempts. End the voice call when explicitly requested and the client provides that control.
