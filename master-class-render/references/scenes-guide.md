# Scenes guide (render layer)

A scenes file (`<source>/scenes/NN.scenes.md`) turns a lesson script's `**Screen:**` descriptions into D2 diagrams that build in sync with the narration. It never changes the script.

## File format
```
# Scenes · NN · <lesson title>

## Beat 1
```d2
direction: right
a: Your code {class: code}
b: Model {class: model}
a -> b: question
# @at "exact phrase from the narration"
c: Tool {class: tool}
b -> c
```
```
- One `## Beat N` per beat in the script, with one ```d2 block (beats may be skipped, but every beat should normally have a diagram).
- `# @at "phrase"`: everything after it appears when the narration reaches the sentence containing that phrase (case-insensitive, matched against the narration with `**`, `*` and backticks removed). Use a short phrase (3–7 words) copied **verbatim** from the beat's own narration, in reading order. Content before the first marker shows at the beat start.
- `# @continue` as the first line: start from the previous beat's final diagram (for beats that extend the same picture).
- The renderer lays out the **final** diagram once and reveals pieces over time, so the layout never jumps.

## Classes (from `prelude.d2`)
`model` (blue: the LLM) · `code` (green: your code / host) · `tool` (orange: tools, servers) · `data` (cylinder) · `person` · `bad` (red: wrong idea, failure) · `good` (green-teal: correct outcome) · `note` (yellow sticky: the conclusion, 3–8 words) · `muted` (dashed, faded) · `wrong` (red dashed edge/label).

## Rules
1. **Draw the idea, don't transcribe the narration.** Labels of 1–6 words. Only sticky notes carry a short sentence.
2. 3–9 shapes per beat. If more are needed, split across `@at` steps or use `@continue` in the next beat.
3. Every beat with more than one sentence should reveal at least 2 steps. Aim for a visible change every ~5–15 s.
4. Ordered lists: a container with `grid-columns: 1` (keeps declaration order). Side-by-side comparisons: two containers.
5. Code/JSON only when the script's Screen shows it; ≤ 6 lines, via `name: |json ... |` or `|python ... |`.
6. Edges: `a -> b: label`. Use `{style.stroke-dash: 3}` for "annotation" links to notes. Use `{class: wrong}` for the "naive / wrong" path.
7. Quotes and special chars in labels: wrap the label in double quotes; escape inner `"` as `\"`. Use `\n` for line breaks. Avoid emoji.
8. Keep ids short and unique within the beat (`llm`, `t1`, `n`). Container children: `box.child: label`.
9. Retrieval-pause beats: show the question as a `note` first; reveal the answer after an `@at` on the answer's first words (after the `…`).
10. Escape `$` as `\$` in labels (D2 treats `$` as a variable).
11. Never put `# @at` inside a `{ }` block: close the container, then add later children with dotted ids (`box.child: ...`).
12. Markdown tables: use `|||md ... |||` (a plain `|md` block ends at the table's first `|`).
13. Style changes (`x.style.fill: ...`) after an `@at` do NOT animate: the final diagram is drawn once, so the change is visible from the start. To show a change, add a new shape (e.g. a red `bad` note) instead.
14. Validate: run the renderer; it must finish with **no** `warning:` lines (each warning = an `@at` phrase not found).

## Validate one lesson quickly
```
cd ~/.copilot/skills/master-class-render/scripts
export PATH=/opt/homebrew/bin:$PATH
.venv/bin/python render.py "<source>/scripts/NN - Title.script.md" "<source>/scenes/NN.scenes.md" /tmp/check.html
```
Must print `ok:` and no `warning:` lines. (First run per lesson synthesises the voice, ~1 min; later runs are cached.)
