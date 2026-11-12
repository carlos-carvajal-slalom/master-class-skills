# Automated/Semi-Automated Educational Video Generation — Research Report (Nov 2026)

## Category 1 — Agentic research systems (LLM plans + codes the video)

**TheoremExplainAgent (TEA)** — academic benchmark/agent, Feb 2025 (updated May 2025). A Planner LLM writes a story plan + narration, a Coder LLM writes Manim Python, producing up to 10-min videos; evaluated on 240 theorems (TheoremExplainBench). Authors explicitly report "challenges remain in visual element layout... spatial reasoning" as the key failure mode — i.e., LLM-authored absolute coordinates in Manim break. Local render (Manim), but planning/coding uses a cloud LLM (model-agnostic). arxiv.org/html/2502.19400, project: tiger-ai-lab.github.io/TheoremExplainAgent.

**Code2Video** (Show Lab, NUS; ICML 2026 accepted) — Planner → Coder → **Critic** (VLM-as-judge) agentic loop generating Manim code, specifically to fix the layout problem TEA identified: the Critic uses "anchor visual prompts" to iteratively correct spatial layout. Ships a benchmark (MMMC) and a "TeachQuiz" pedagogical-transfer metric. Open source, ~2k GitHub stars as of Aug 2026, MIT-style repo. This is the closest published blueprint to what the user wants (code-centric, auto-corrected layout, Manim render, local-executable). github.com/showlab/Code2Video, showlab.github.io/Code2Video, arxiv.org/abs/2510.01174.

**Paper2Video / PaperTalker** (Show Lab, NUS, Oct 2025) — turns a paper + photo + voice sample into a full presentation video (slides+subtitles+speech+talking head), multi-agent ("Tree Search Visual Choice", cursor grounding). Good analog for "notes → full video" but optimized for slide decks with avatar, not progressive diagram builds; uses commercial-style TTS/talking-head pipeline (cloud-dependent for the talker). ~2.3k stars, active, Apache/MIT-ish license. github.com/showlab/Paper2Video, arxiv.org/abs/2510.05096.

**PresentAgent** (EMNLP 2025 Demo) — multimodal agent turning long documents into narrated presentation videos (slides + TTS + optional avatar). Early-stage research code, not a turnkey CLI; local feasibility unverified for the avatar component. github.com/AIGeeksGroup/PresentAgent.

**Verdict on this category**: mature as *research validation* that "LLM writes renderable code (mostly Manim) → render locally" is the state-of-the-art pattern for pedagogical video, and that **layout/coordinate authoring by the LLM is the dominant failure mode** across all three papers — directly relevant to the user's priority #1. None of these ship as a drop-in CLI skill; they're reference architectures to borrow from, not install.

## Category 2 — Programmatic animation/video frameworks (the render layer)

**Manim + manim-voiceover** — Manim (community edition) is the de facto academic-explainer renderer; **manim-voiceover** is the key plugin for this user's constraint #1: it exposes a `tracker` context whose `get_remaining_duration()` lets code `self.wait()` for exactly as long as the TTS audio takes, so **timing is derived from audio, not hand-authored frame counts**. It also supports Whisper-based per-word bookmarks for word-level animation triggers. TTS backends: Gemini TTS, Azure, gTTS, pyttsx3 (local) — Kokoro/Piper aren't built in but can be wired in via the generic TTS service interface since it just needs an audio file + duration. Fully local-renderable (Python, ffmpeg), MIT-ish license, mature (manim.community, docs at voiceover.manim.community). Pitfall: scene composition (`next_to`, `arrange`, `shift`) still requires the LLM to write Python geometry — exactly the flaw TEA/Code2Video found. Mitigation: constrain the agent to *relative* layout primitives (`next_to`, `arrange`, `VGroup`) instead of absolute coordinates, which removes most coordinate-token overhead. github.com/ManimCommunity/manim-voiceover.

**Remotion + official "Claude Code skill"** — Remotion ships a documented AI/skills integration (remotion.dev/docs/ai/skills) and community templates like `jhartquist/claude-remotion-kickstart`, which bundles slash-commands for AI image/video gen (Replicate), transcription (Deepgram), and voiceover (ElevenLabs via MCP), plus **"transcript-based timing"**: word-level timestamps drive `<Sequence>` offsets automatically. Strong engineering ecosystem, renders true MP4 via headless Chromium. Pitfalls per a 2026 walkthrough: video-as-pure-function-of-frame-number means **the LLM must still reason in frame math** (`useCurrentFrame`, `interpolate()`), and missing `from` offsets on `<Sequence>` is the most common agent bug; default integrations (ElevenLabs, Deepgram, Replicate) are cloud — must be swapped for local TTS/transcription to meet the data-sensitivity constraint. github.com/jhartquist/claude-remotion-kickstart; blog.openreplay.com/making-videos-claude-code-remotion.

**Motion Canvas** — TypeScript, generator-function animation model, built specifically "to synchronize [vector animations] with voice-overs," with a visual editor. Scenes are still manually positioned nodes, but signals/tweens reduce boilerplate vs. raw coordinates. Rendering is editor/UI-triggered (less headless/CLI-friendly than alternatives). github.com/motion-canvas/motion-canvas.

**Revideo** — a Motion-Canvas-derived fork optimized for headless, programmatic rendering (no editor dependency), reportedly ~10x faster rendering, multi-track audio with precise placement, MIT license, explicitly markets itself as LLM-codeable ("A scene is plain TypeScript, so Claude or Codex can produce one from a prompt"). Best "escape hatch" if the user prefers a TS/Node stack over Python. github.com/midrender/revideo (formerly redotvideo/revideo).

**Slidev / reveal.js + audio** — not deeply investigated here per instructions to avoid anchoring, but worth noting: fragment-based reveal (`v-click`/`.fragment`) gives progressive builds "for free" with zero coordinate authoring, and narration timing can be derived purely from per-slide/per-fragment audio-clip durations (ffprobe), which is the *lowest-token* approach for text/diagram-heavy lessons that don't need true animation (morphing shapes, camera moves).

## Category 3 — Local TTS options (constraint #3)

- **macOS `say`** — free, zero setup, robotic but usable for internal study material.
- **Piper** — fastest, smallest, most synthetic-sounding; sub-second latency even on CPU (contracollective.com/blog/kokoro-vs-piper-vs-xtts-local-text-to-speech-m5-max-2026).
- **Kokoro-82M** — Apache-2.0, 82M params, "surprisingly natural" per multiple 2026 benchmarks, 1–2s/utterance on CPU, <1s on modest GPU — best naturalness/cost tradeoff for narration (github.com/hexgrad/kokoro; contracollective.com, bigiron.cc comparisons).
- **XTTS v2 / F5-TTS** — voice cloning, higher latency/memory, best for batch (non-live) narration synthesis — fine for this offline-rendering use case.
All four are local-only with no data leaving the machine, directly meeting the corporate-sensitivity requirement — unlike ElevenLabs/Azure/Gemini TTS defaults baked into manim-voiceover and the Remotion template.

## Category 4 — Commercial/hosted (flagged, not recommended)

**NotebookLM Video Overviews** (Google) — one-click notes→video, zero engineering, but fully cloud, no scripting control over pedagogy/visuals, and **sources are uploaded to Google** — disqualifying given the user's custom pedagogy skill and data-sensitivity flag (support.google.com/gemininotebook/answer/16454555). **Synthesia/HeyGen/Colossyan/Descript** — all cloud SaaS with per-minute costs and third-party data exposure; unverified fit, not investigated further since excluded by constraint #3.

## Ranked Shortlist

1. **Manim + manim-voiceover** (relative-layout constrained) — best pedagogical fidelity (true progressive diagram builds, camera moves, morphing — directly supports Mayer's principles), audio-derived timing (no hand-authored frame numbers), fully local with Kokoro/Piper swapped in, validated by two independent 2025 research papers as the leading approach for "LLM-authored educational video." Main cost: agent still writes Python object code, so the render-skill must mandate `next_to()`/`arrange()` idioms and ban absolute coordinates to hit token/coordinate-minimization goal.
2. **D2-style declarative diagram + reveal.js/Slidev fragments + custom audio-duration sync script** — lowest LLM-token footprint of any option (markdown + diagram DSL only, zero coordinates, zero frame math), self-contained HTML output, but weaker for continuous motion/morphing — best for notebook/markdown-heavy "MCP tool-use" lab content that is mostly diagrams + code blocks, not physics-style animation.
3. **Revideo** — if the user prefers a TypeScript/Node stack; headless, fast, MIT, LLM-codeable by design, but still coordinate-based scene code.
4. **Remotion + official skill + local-TTS swap** — most mature agent tooling/community support (first-party Claude Code skill, transcript-timing pattern), but frame-math authoring burden and default-cloud integrations must be reconfigured.
5. (Not recommended) **NotebookLM Video Overviews** — reference only, cloud + zero pedagogical control.

## Suggested Architecture (Option 1: Manim + manim-voiceover)

```
Pedagogy skill → Script (markdown: narration text + ordered "beats",
                 each beat = {narrate, show/highlight/morph-to <ref>})
     ↓
Render-skill (this deliverable) compiles beats into:
  (a) narration text chunks  → local TTS (Kokoro, fallback `say`) → per-beat .wav
  (b) a thin Manim Scene using ONLY relative layout calls
      (VGroup, next_to, arrange, Transform) keyed by beat id — no
      pixel coords, no frame numbers authored by the LLM
     ↓
manim-voiceover `tracker` plays each beat's .wav and the scene
`self.safe_wait(tracker.get_remaining_duration())` — sync is
derived from actual audio length, eliminating manual timing tokens
     ↓
`manim -qh` renders MP4 locally (ffmpeg); optional thin HTML wrapper
adds chapter markers from beat boundaries for a self-contained player
```

This keeps the LLM's authored surface to narration + a short beat list (what to show/highlight/morph), delegates all coordinate math to Manim's auto-layout primitives, and derives all timing from local TTS audio — directly satisfying constraints #1–#4, while being installable as a CLI/Copilot skill (constraint #5) by packaging the beat-DSL compiler + Manim scene template as a single invocable script.

**Gaps/unverified**: manim-voiceover's native TTS adapters don't include Kokoro/Piper out of the box — wiring them in via its generic TTS-service interface is plausible from the architecture but not confirmed by a working example in sources reviewed. Code2Video's full agent code (Planner/Coder/Critic prompts) wasn't read line-by-line — only README/paper-level claims verified.