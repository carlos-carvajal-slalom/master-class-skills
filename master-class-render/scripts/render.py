#!/usr/bin/env python3
"""Render a lesson script (+ scenes file) into a self-contained narrated HTML player.

Usage: render.py <lesson.md> <scenes.md> <out.html> [--voice am_michael] [--speed 1.0] [--lang en-us]
"""
import argparse, base64, hashlib, html, json, os, re, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).parent
MODEL_DIR = Path.home() / ".cache" / "kokoro"
CACHE = HERE / ".cache"
SR = 24000
GAP_SENTENCE, GAP_PARAGRAPH, GAP_BEAT, THINK_PAUSE = 0.25, 0.55, 0.9, 4.0

PRELUDE = (HERE / "prelude.d2").read_text()


# ---------- parsing ----------
def parse_script(text):
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    beats = []
    for m in re.finditer(r"^### Beat (\d+) · (.+?)\n(.*?)(?=^### Beat |\Z)", text, re.S | re.M):
        body = m.group(3)
        narr = re.search(r"\*\*Narration:\*\*\n(.*)", body, re.S)
        paras = [p.strip() for p in (narr.group(1) if narr else "").strip().split("\n") if p.strip()]
        beats.append({"n": int(m.group(1)), "title": m.group(2).strip(), "paras": paras})
    return title, beats


def parse_scenes(text):
    scenes = {}
    for m in re.finditer(r"^## Beat (\d+)\s*\n.*?```d2\n(.*?)```", text, re.S | re.M):
        scenes[int(m.group(1))] = m.group(2)
    return scenes


def split_steps(src):
    """Split a scene into steps on '# @at "phrase"' markers. Returns (continue?, [(phrase|None, chunk)])."""
    cont = bool(re.match(r"\s*# @continue", src))
    steps, phrase, buf = [], None, []
    for line in src.splitlines():
        m = re.match(r'\s*# @at "(.+)"', line)
        if m:
            steps.append((phrase, "\n".join(buf)))
            phrase, buf = m.group(1), []
        elif not line.strip().startswith("# @continue"):
            buf.append(line)
    steps.append((phrase, "\n".join(buf)))
    return cont, steps


# ---------- text for display and speech ----------
def display_text(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", s)
    return s.replace("`", "")


def speech_text(s, lang="en-us"):
    s = display_text(s)
    if lang.startswith("en"):
        s = re.sub(r"\b[A-Z]-(\d\d)(\d\d)\b", lambda m: f"{m.group(0)[0]} {int(m.group(1))} {'oh ' + str(int(m.group(2))) if m.group(2)[0] == '0' else int(m.group(2))}", s)
    s = re.sub(r"(?<=[a-z])_(?=[a-z])", " ", s)
    s = re.sub(r"(?<=[a-z])([A-Z])", lambda m: " " + m.group(1).lower(), s)
    if lang.startswith("en"):
        s = s.replace("→", " to ").replace("×", " times ").replace("e.g.", "for example")
    else:
        s = s.replace("→", ", ").replace("×", " por ")
    s = s.replace("—", ", ")
    return re.sub(r"\s+", " ", s).strip()


def sentences(para):
    """Yield ('say', text) and ('think', None) items for a paragraph."""
    for i, part in enumerate(re.split(r"\s*…\s*", para)):
        if i:
            yield ("think", None)
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", part.strip()):
            if s.strip():
                yield ("say", s.strip())


# ---------- TTS ----------
class TTS:
    def __init__(self, voice, speed, lang):
        from kokoro_onnx import Kokoro
        self.k = Kokoro(str(MODEL_DIR / "kokoro-v1.0.onnx"), str(MODEL_DIR / "voices-v1.0.bin"))
        self.voice, self.speed, self.lang = voice, speed, lang

    def say(self, text):
        key = hashlib.sha1(f"{self.voice}|{self.speed}|{self.lang}|{text}".encode()).hexdigest()
        f = CACHE / "tts" / f"{key}.npy"
        if f.exists():
            return np.load(f)
        audio, sr = self.k.create(text, voice=self.voice, speed=self.speed, lang=self.lang)
        assert sr == SR
        f.parent.mkdir(parents=True, exist_ok=True)
        np.save(f, audio)
        return audio


# ---------- diagrams ----------
def d2_svg(src, layout):
    key = hashlib.sha1(f"{layout}|{src}".encode()).hexdigest()
    f = CACHE / "d2" / f"{key}.svg"
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", suffix=".d2", delete=False) as t:
            t.write(src)
        r = subprocess.run(["d2", "--sketch", "--pad", "30", "--layout", layout, t.name, str(f)], capture_output=True, text=True)
        os.unlink(t.name)
        if r.returncode:
            raise SystemExit(f"d2 failed:\n{r.stderr}\n--- source ---\n{src}")
    return f.read_text()


STAGE_W, STAGE_H = 1090, 610


def fit_scale(svg):
    m = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', svg)
    return min(STAGE_W / float(m.group(1)), STAGE_H / float(m.group(2))) if m else 1.0


def best_layout_svg(src, layout):
    """Render src; if it fits the 16:9 stage poorly, try the other root direction and keep the larger one."""
    svg = d2_svg(src, layout)
    if fit_scale(svg) >= 0.7:
        return svg
    flips = {"right": "down", "down": "right", "left": "up", "up": "left"}
    m = re.search(r"^direction: (\w+)\s*$", src, re.M)
    cur = m.group(1) if m else "down"
    if cur not in flips:
        return svg
    alt_src = re.sub(r"^direction: \w+\s*$", f"direction: {flips[cur]}", src, count=1, flags=re.M) if m else f"direction: {flips[cur]}\n{src}"
    alt = d2_svg(alt_src, layout)
    return alt if fit_scale(alt) > fit_scale(svg) * 1.1 else svg


def svg_ids(svg):
    return sorted(set(re.findall(r'<g class="([A-Za-z0-9+/=]+)[ "]', svg)) - {"shape"})


def clean_svg(svg):
    svg = re.sub(r"<\?xml[^>]*>", "", svg)
    return re.sub(r'<svg ', '<svg preserveAspectRatio="xMidYMid meet" ', svg, count=1)


# ---------- build ----------
def build(args):
    script = Path(args.lesson).read_text()
    title, beats = parse_script(script)
    scenes = parse_scenes(Path(args.scenes).read_text()) if args.scenes else {}
    tts = TTS(args.voice, args.speed, args.lang)

    audio, t = [], 0.0
    captions, chapters, steps, svgs = [], [], [], []
    prev_src = ""

    def add(chunk):
        nonlocal t
        audio.append(chunk)
        t += len(chunk) / SR

    def silence(sec):
        add(np.zeros(int(sec * SR), dtype=np.float32))

    for b in beats:
        chapters.append({"t": round(t, 2), "title": f"{b['n']} · {b['title']}"})
        src = scenes.get(b["n"])
        step_ids, phrases = [], []
        if src:
            cont, parts = split_steps(src)
            base = prev_src if cont else ""
            acc = base
            for phrase, chunk in parts:
                acc = acc + "\n" + chunk
                step_ids.append(svg_ids(d2_svg(PRELUDE + acc, args.layout)))
                phrases.append(phrase)
            prev_src = acc
            svgs.append(clean_svg(best_layout_svg(PRELUDE + acc, args.layout)))
            steps.append({"t": round(t, 2), "svg": len(svgs) - 1, "ids": step_ids[0]})
        pending = list(range(1, len(phrases)))
        for pi, para in enumerate(b["paras"]):
            for kind, s in sentences(para):
                for k in list(pending):
                    if phrases[k] and s and phrases[k].lower() in display_text(s).lower():
                        steps.append({"t": round(t, 2), "svg": len(svgs) - 1, "ids": step_ids[k]})
                        pending.remove(k)
                if kind == "think":
                    captions.append({"t": round(t, 2), "text": "⏸ Pause and think…", "think": True})
                    silence(THINK_PAUSE)
                    continue
                captions.append({"t": round(t, 2), "text": display_text(s)})
                add(tts.say(speech_text(s, args.lang)))
                silence(GAP_SENTENCE)
            silence(GAP_PARAGRAPH - GAP_SENTENCE)
        for k in pending:
            print(f"warning: beat {b['n']}: phrase not found: {phrases[k]!r}", file=sys.stderr)
            steps.append({"t": round(t - 0.5, 2), "svg": len(svgs) - 1, "ids": step_ids[k]})
        silence(GAP_BEAT)

    stem = hashlib.sha1(str(Path(args.out).resolve()).encode()).hexdigest()[:10]
    wav = CACHE / f"lesson-{stem}.wav"
    sf.write(wav, np.concatenate(audio), SR)
    mp3 = CACHE / f"lesson-{stem}.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "64k", "-ac", "1", str(mp3)], check=True)
    audio_b64 = base64.b64encode(mp3.read_bytes()).decode()

    steps.sort(key=lambda s: s["t"])
    data = {"title": title, "course": args.course, "duration": round(t, 2), "chapters": chapters,
            "captions": captions, "steps": steps, "svgs": svgs}
    page = (HERE / "player.html").read_text()
    page = page.replace("__TITLE__", html.escape(title)).replace("__DATA__", json.dumps(data)).replace("__AUDIO__", audio_b64)
    Path(args.out).write_text(page)
    print(f"ok: {args.out} · {t/60:.1f} min · {len(chapters)} beats · {len(svgs)} diagrams · {len(steps)} steps")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("lesson"); p.add_argument("scenes"); p.add_argument("out")
    p.add_argument("--voice", default="am_michael"); p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--lang", default="en-us"); p.add_argument("--layout", default="elk")
    p.add_argument("--course", default="")
    build(p.parse_args())
