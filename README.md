# Study Buddy

Study Buddy is a Codex skill for people preparing for certification exams. Bring a question bank, answer key, course slides, or study guide. It can coach you through a mock one question at a time, explain a difficult topic, and turn a course into a visual revision document. Your study files and progress live in your workspace.

## Claude

Download the [Claude upload ZIP](https://github.com/nikhilgs817/study-buddy/raw/refs/heads/main/claude/study-buddy.zip). In Claude, enable code execution, open **Customize > Skills**, choose the upload option, and enable Study Buddy. Attach a bank and ask "Use Study Buddy to quiz me from question 1." Upload your saved progress when moving to a fresh chat. The [Claude edition](claude/study-buddy/) includes the question lookup helper, diagram example, review workflows and voice score preferences. [Anthropic setup instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

## ChatGPT account

On an eligible account, open **Plugins > Skills > Add > Upload from your computer**, upload the skill folder as a ZIP, and install it if prompted. Check the Installed collection. Availability depends on your workspace. [OpenAI Skills guide](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)

## Codex setup

You need Codex with access to a local workspace. Git is used for the installation below. The included question lookup helper uses Python 3.7+ and its standard library. For PDFs, slides, and document export, Study Buddy uses the document tools available in your Codex environment.

Clone the repository into a convenient directory and copy its `study-buddy` folder into your user skills directory. In Windows PowerShell:

```powershell
git clone https://github.com/nikhilgs817/study-buddy.git
$skillsDir = Join-Path $env:USERPROFILE '.codex/skills'
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
Copy-Item -Recurse -Force -Path './study-buddy/study-buddy' -Destination $skillsDir
```

On macOS or Linux:

```sh
git clone https://github.com/nikhilgs817/study-buddy.git
mkdir -p ~/.codex/skills/study-buddy
cp -R study-buddy/study-buddy/. ~/.codex/skills/study-buddy/
```

If you have local edits to an older version, save a copy first. For an update, pull the latest main branch in the checkout and repeat the copy step. The installed entry point should be `~/.codex/skills/study-buddy/SKILL.md`. Open a new Codex chat in your study workspace, attach your materials or give their paths, and invoke `$study-buddy`. To check installation without starting a quiz, ask “$study-buddy, what can I say?”

## Start practicing

> $study-buddy Start a sequential practice session with the attached mock and key. Begin at question 1, ask one question at a time, and wait for my answer.

The coach indexes the bank, preserves its printed numbering and option order, and grades each submitted response. Ask for a hint, flag a question, or say “B for ball, guess.” After grading, say “next.” Say “pause” to save or “handover” to get a prompt for a fresh chat. In the same workspace, “$study-buddy Resume my saved session” restores the active item and delivery preferences.

## Voice practice and mock review

Open the client's voice control when available. Read and show is the default. You can also explicitly request another delivery style.

- **Read and show.** “Show the exact question and choices in chat and read that same text. Let me answer by voice.”
- **Show only, answer by voice.** “Display the bank question once. I'll answer aloud. Speak only the feedback.” This works well when live narration has been changing the wording.
- **Review a completed mock.** “Here are my responses and key. Review my misses and guesses by voice, one at a time. Hide my previous choice until I answer again.”

If live narration changes the item or option order, say “wrong question.” Study Buddy reopens the printed item and asks again before grading. The app controls speech playback. For verbatim playback, use Read Aloud on the displayed question if available.

After an answer, you hear one verdict and a brief reason. The running score appears in chat. By default you hear the score every ten newly graded first attempts, when the mock ends, or whenever you ask “How am I doing?” Say “Only show my score” or “Read my score every five answers” to change that. Say “next” to hear the next question directly, or “repeat” to hear the current item again.

## Create study materials

| Ask for | Example request |
| --- | --- |
| Visual cheat sheet | “Make a printable PDF from these slides. Draw the architecture, expand the acronyms, compare similar tools, include slide numbers and add memory cues.” |
| Study document | “Create a study guide by exam objective. For each topic give a diagram, a worked example from DevOps, and a recall question.” |
| Concept explanation | “Explain numerical range versus precision with a small example. Give me a mnemonic, then take me back to the same question.” |
| Mock audit | “Map these questions to the official exam objectives. List gaps and ambiguous keys with question numbers.” |
| Key challenge | “Why isn't my answer valid? Check current official documentation and use corrected technical grading.” |

## Progress and privacy

The coach keeps the selected bank, quiz position, attempts, flags, guesses, and prior corrections in your study workspace. A fresh chat can resume from that workspace or a handover. Review attempts are tracked separately, and a corrected spoken answer updates its original attempt. To practice privately, use a workspace outside this repository and keep your PDFs, extracted bank, and progress files there.

The installed behavior lives in the [skill instructions](study-buddy/SKILL.md). The [study workflows](study-buddy/references/study-workflows.md) describe how the coach prepares study documents and debriefs mocks. See the [worked Triton architecture and request flow](study-buddy/references/triton-example.md) for an example.
