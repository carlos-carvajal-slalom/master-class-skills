---
name: master-class-render
description: Render master-class lesson scripts into narrated hand-drawn diagram videos (MP4, 1080p, burned-in captions, local Kokoro voice) plus Obsidian lesson notes and a course MOC. Companion of the master-class skill; use after scripts exist in <source>/scripts/, or to re-render/fix an existing course.
argument-hint: path to the course source folder (contains scripts/ and scenes/)
---

# Master class render

Input: `<source>/scripts/NN - Title.script.md` (written by **master-class**).
You write: `<source>/scenes/NN.scenes.md` (D2 text, no coordinates, no timings).
One command produces: `<videos>/NN - Title.mp4` + `<notes>/NN - Title.md` + `<notes>/<MOC>.md`.

Everything runs locally: D2 lays out diagrams (sketch style), Kokoro-82M speaks, timing comes from the real audio, Chromium captures one frame per visual change, ffmpeg encodes. Nothing is sent to third parties. The only tokens spent are the scenes files (~1× the script size).

## 0 · Setup (once per machine; re-run is safe)
```bash
bash ~/.copilot/skills/master-class-render/scripts/setup.sh
```
Installs `d2`, `ffmpeg`, `uv` (Homebrew), a venv in `scripts/.venv` with kokoro-onnx, soundfile and playwright (Chromium), and the Kokoro model in `~/.cache/kokoro` (~350 MB). If `scripts/.venv/bin/python` exists, setup is done.

## 1 · Write the scenes
Read [references/scenes-guide.md](references/scenes-guide.md) and the approved examples first: [01](examples/01.scenes.md), [05](examples/05.scenes.md), [08](examples/08.scenes.md). Each is paired with its script in `~/.copilot/skills/master-class/examples/`, so you can see exactly how each **Screen** became a diagram. This step runs fine on a small/fast model: work one lesson at a time and let the validator tell you when it is right. Then, for each script, one `## Beat N` + one ```d2 block per beat, translating the beat's **Screen** description:
- `# @at "phrase"` (3–7 words copied verbatim from that beat's narration) reveals what follows when the narrator says it. The final layout is computed once, so nothing jumps; new pieces glow briefly.
- `# @continue` extends the previous beat's diagram.
- Classes: `model`, `code`, `tool`, `data`, `person`, `bad`, `good`, `note` (sticky with the conclusion; these become the lesson note's **Key ideas**), `muted`, `wrong`.
- The guide lists the D2 gotchas (`\$`, no `@at` inside `{}` blocks, `|||md` tables, style changes don't animate).

Validate each lesson as you go (must print `ok:` and no `warning:`):
```bash
cd ~/.copilot/skills/master-class-render/scripts && export PATH=/opt/homebrew/bin:$PATH
.venv/bin/python render.py "<source>/scripts/NN - Title.script.md" "<source>/scenes/NN.scenes.md" /tmp/check.html
```
Many lessons → split across parallel sub-agents (≈4 lessons each) with the guide and the example.

## 2 · Build the course
```bash
cd ~/.copilot/skills/master-class-render/scripts && export PATH=/opt/homebrew/bin:$PATH
.venv/bin/python build_course.py \
  --source "<lab>/_attachments/master-class/source" \
  --videos "<lab>/_attachments/master-class" \
  --notes  "<lab>/Master class" \
  --moc    "<Lab name> · Master class" \
  --course "<label shown top-left in the video>" \
  --tags   "course/<course-tag>,section/labs,topic/<x>,type/lesson" \
  --intro  "One paragraph for the MOC: what the course is built from ([[source note links]]) and its intent." \
  --voice am_michael --lang en-us
```
- Language/voice: English `--voice am_michael --lang en-us` (alternatives `am_puck`, `bm_george --lang en-gb`); Spanish `--voice em_alex --lang es` (female: `ef_dora`).
- `--only 03,07` rebuilds selected lessons (notes are always regenerated for all). `--notes-only` regenerates notes without video.
- ~15 s per lesson after the voice is cached (first synthesis ≈ 1 min per lesson). Outputs are encoded in a temp folder and copied, because writing directly into OneDrive-synced folders times out.
- Match `--tags` to the tags used by the source notes.

## 3 · Verify before reporting
- The build printed `ok:` for every lesson and no `!! … @at phrase(s) not found`.
- Extract 2 frames from one or two MP4s and look at them (use a **new file name each time**; image viewers cache):
  `ffmpeg -v error -ss 120 -i "<mp4>" -frames:v 1 -vf scale=1280:-1 /tmp/mc_check_<n>.png`
  Check: the diagram is readable (not a tiny strip), the caption matches, the right beat is shown.
- Diagram too small? The renderer already tries the other layout direction automatically; if still small, split the beat's diagram or drop `@continue` and summarise earlier steps in one `muted` box.
- Open the MOC note and one lesson note: video embed `![[NN - Title.mp4]]`, Goal, Key ideas, Check yourself (question + folded answer), folded Transcript, prev/next links.

## What each lesson note contains (generated, zero tokens)
Frontmatter (tags, lesson, duration, course link) · embedded MP4 · Goal · misconception · Key ideas (from `note` stickies) · Check yourself (from the `Retrieval pause` beat) · folded transcript · ← prev · Course index · next →.

## Files
`scripts/`: `build_course.py` (entry point) · `render.py` (script + scenes → intermediate HTML with audio and timeline) · `export_mp4.py` (HTML → MP4) · `make_notes.py` (notes + MOC) · `player.html` (intermediate template; also a usable offline player) · `prelude.d2` (classes, font sizes) · `setup.sh`. Caches: `scripts/.cache/` (voice clips, diagrams; safe to delete).
