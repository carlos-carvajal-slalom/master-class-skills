---
name: master-class
description: Turn a course lab, note or folder (Obsidian notes, notebooks, code) into a full narrated video master class stored in the same Obsidian vault - one MP4 + one note per lesson + a course index (MOC). Teaches the course's intent (problem before solution, misconceptions, intuition, limits), not line-by-line code. Use when asked to "make a master class / course / video lessons / tutorial videos" from study material.
argument-hint: path to the lab, note or folder; optional output language
---

# Master class

Turns study material into a video course the learner would actually watch. This skill owns the **pedagogy** (reading, course map, scripts). Rendering (diagrams, voice, MP4, Obsidian notes) is done by the companion skill **master-class-render**.

## Model routing (the user's explicit instruction)

```
PEDAGOGY_MODEL: claude-sonnet-5.5    # reading, course map, scripts (steps 1–4). Cheapest model that keeps the quality; change here if needed.
```

Quality depends almost entirely on steps 1–4, so they **must run on PEDAGOGY_MODEL**. Steps 0, 5 and 6 are mechanical and run on whatever model is driving this session.

- **If you are already running as PEDAGOGY_MODEL** (or the user says to skip delegation), do steps 1–4 yourself.
- **Otherwise, delegate.** Launch a `general-purpose` sub-agent with `model: PEDAGOGY_MODEL`. Setting the model here is the user's explicit request. Its prompt must include: the source path, output language, the source folder path, any focus/context the user gave, and *"Read ~/.copilot/skills/master-class/SKILL.md and follow steps 1–2 exactly; write course-map.md, then stop and return the map."*
  - Show the returned map to the user and wait for approval (unless the user asked to run without approvals).
  - Then send the approval/changes to **the same agent** (`write_agent`): *"Approved [+ changes]. Now do steps 3–4 exactly: write every script, lint until no errors, write scripts/README.md, then return the lint summary."*
  - Then continue yourself with step 5 (render), which needs no big model.
- If the user names a different model for pedagogy in the request, use that one instead.

## Reading list (before writing anything)
1. [references/cheatsheet.md](references/cheatsheet.md): one page with the rules that matter.
2. [references/learner-profile.md](references/learner-profile.md): who the learner is, how he thinks, which analogies land.
3. [references/lesson-template.md](references/lesson-template.md): the fill-in skeleton for every lesson.
4. Approved examples, all from one course (Lab 02, Tool Use & MCP): [examples/course-map.md](examples/course-map.md), [01](examples/01%20-%20The%20model%20never%20runs%20anything.script.md) (a wrong sentence → mechanism), [05](examples/05%20-%20Retrying%20without%20paying%20twice.script.md) (a story → a rule), [08](examples/08%20-%20Why%20MCP%20exists.script.md) (weighing options → why a standard exists). Imitate their depth and voice, not their wording.
5. Optional: [references/teaching-research.md](references/teaching-research.md), the evidence and sources behind the rules.

## Non-negotiable teaching rules
1. **Problem before solution.** Every lesson opens with a concrete situation where something fails or hurts. The technology is named only after the problem and the rejected obvious alternatives.
2. **Teach the intent, not the implementation.** If the material teaches X, the learner must understand what X is, why it exists, when to use it and when not to. Code is evidence for a concept already explained (≤ 6 lines), never a walkthrough.
3. **Take apart one misconception per lesson**, out loud.
4. **Concrete → abstract**, with one running example threading the whole course.
5. **The learner's way of thinking**: context → real constraint → options considered and why each was rejected → decision → cost/trade-off → when not to use it. Ask "is there something better?" explicitly.
6. **Retrieval pause** in every lesson: question → `…` (the renderer inserts a 4 s pause) → answer with its reason.
7. **Bridge**: every lesson ends with the problem the next one solves.
8. **No length limit**, but one learning goal per lesson (typically 4–6 min).
9. **Vary** openings, threads and closings; never a fixed mould.
10. **Never invent facts or numbers.** Technical claims come from the sources read or verified official docs; hypothetical scenarios must be clearly scenarios.

## Workflow

### 0 · Ask first
- **Output language**: always ask unless the user already said it.
- Source path, if missing. Defaults (confirm only if the vault layout differs):
  - notes → `<lab folder>/Master class/`
  - videos → `<lab folder>/_attachments/master-class/`
  - sources → `<lab folder>/_attachments/master-class/source/` (`course-map.md`, `scripts/`, `scenes/`)
- Apply **Model routing** above.

### 1 · Read with bounded depth
- Read the lab/note fully. For notebooks, read the markdown and the concepts the code demonstrates; never execute notebooks and never read secrets or `.env`.
- Follow `[[wikilinks]]`/linked docs **up to 2 levels deep**, only if relevant to the material's intent. Skip future labs, already-covered prerequisites and tangents.
- Web is allowed to verify or complete the *why* (official docs and specs). Cite it.
- Keep a log: read / discarded + reason.

### 2 · Course map → **stop for approval**
Write `<source>/course-map.md` like [examples/course-map.md](examples/course-map.md):
- the intent in 2–3 sentences, as what the learner will be able to **decide**;
- the reading log;
- a lesson table: `# · lesson · problem it opens · misconception · analogy/opening · resolves → leaves open`, with lesson 00 as the big picture and the last lesson as the synthesis as decisions.

### 3 · Scripts, one lesson per pass
For each lesson, in order:
1. Re-read the cheatsheet, the template, the lesson's row in the map and one example.
2. Copy [references/lesson-template.md](references/lesson-template.md) to `<source>/scripts/NN - Short title.script.md` and fill it in. The `.script.md` suffix is required, because otherwise Obsidian confuses scripts with lesson notes.
3. Lint it (step 4) and fix it before moving to the next lesson.

Narration is written for the ear: no lists, tables or URLs; numbers as people say them; ids/code in backticks (read as words). The retrieval beat is titled `Retrieval pause` and has `…` between question and answer. If its Screen is the question itself, write it as `*"question"*`.

Finally write `<source>/scripts/README.md`: lesson table + rubric self-review.

### 4 · Lint + rubric (must pass before rendering)
```bash
python3 ~/.copilot/skills/master-class/scripts/lint_script.py "<source>/scripts" --sources "<lab folder>" <other notes read>
```
Fix every **ERROR**. Fix every **WARN** unless it's intended (for example, a hypothetical number in a clearly hypothetical scenario). The linter can't judge these, so check them yourself:
- [ ] Why before how: the technology appears only after the rejected alternatives
- [ ] Understandable without seeing any code
- [ ] The misconception is stated and taken apart explicitly
- [ ] The Hook's question is answered explicitly
- [ ] The Screen complements the narration (no duplicated text)
- [ ] Read aloud, it sounds like a teacher, not bullets
- [ ] Openings/closings vary between consecutive lessons

### 5 · Render → **master-class-render**
Read `~/.copilot/skills/master-class-render/SKILL.md` and follow it: write the scenes, then build the MP4s, lesson notes and MOC with one command, then verify.

### 6 · Report
Paths (MOC first), lesson count and total duration, lint result, anything unverified, and a summary of the reading log.
