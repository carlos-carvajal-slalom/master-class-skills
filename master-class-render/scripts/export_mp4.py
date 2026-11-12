#!/usr/bin/env python3
"""Export rendered lesson HTML files to MP4 (1080p, burned-in captions).

Usage: export_mp4.py <out_dir> <lesson.html> [<lesson.html> ...]
Each lesson becomes <out_dir>/<same name>.mp4. Captures one frame per visual change, then ffmpeg joins them with the audio.
"""
import base64, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

GLOW = 1.2
W, H, STAGE_H = 1920, 1080, 890

EXPORT_CSS = f"""
*, *::before, *::after {{ transition: none !important; animation: none !important; }}
body {{ display:block; background:#fffdf7; width:{W}px; height:{H}px; overflow:hidden; }}
header, #bar, #controls, aside, #start {{ display:none !important; }}
#stage {{ position:absolute; left:0; top:0; width:{W}px; height:{STAGE_H}px; margin:0; border-radius:0; box-shadow:none; }}
#stage .frame {{ padding:40px 60px 20px; }}
#chapterTitle {{ font-size:22px; top:18px; left:26px; }}
#cap {{ position:absolute; left:0; top:{STAGE_H}px; width:{W}px; height:{H - STAGE_H}px; margin:0; padding:0 120px;
        font-size:38px; line-height:1.3; background:#f1efe9; border-top:1px solid #e9e4d8; }}
g.glow {{ filter: drop-shadow(0 0 10px #fab005); }}
"""

SET_STATE = """([t, glow]) => {
  curStep = -2; shown = new Set(); render(t);
  document.querySelectorAll('g.glow').forEach(g => g.classList.remove('glow'));
  const m = groups[curFrame]; if (m) glow.forEach(id => (m.get(id) || []).forEach(g => g.classList.add('glow')));
}"""


def events(D):
    steps = D["steps"]
    glow_at, prev_by_svg = [], {}
    for s in steps:
        prev = prev_by_svg.get(s["svg"])
        new = sorted(set(s["ids"]) - set(prev)) if prev is not None else []
        prev_by_svg[s["svg"]] = s["ids"]
        if new:
            glow_at.append((s["t"], s["t"] + GLOW, new))
    times = {0.0, *[s["t"] for s in steps], *[c["t"] for c in D["captions"]], *[c["t"] for c in D["chapters"]]}
    times |= {round(e, 2) for _, e, _ in glow_at}
    times = sorted(t for t in times if t < D["duration"])
    out = []
    for t in times:
        glow = next((ids for s, e, ids in glow_at if s <= t < e), [])
        out.append((t, glow))
    return out


def export(page, html_path, out_mp4):
    text = html_path.read_text()
    D = json.loads(re.search(r"const D = (\{.*\});\n", text).group(1))
    audio = base64.b64decode(re.search(r'data:audio/mpeg;base64,([^"]+)"', text).group(1))
    page.goto(html_path.as_uri())
    page.add_style_tag(content=EXPORT_CSS)
    page.evaluate("window.requestAnimationFrame = () => 0")  # stop the player's audio-driven loop
    page.wait_for_timeout(300)
    ev = events(D)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "audio.mp3").write_bytes(audio)
        lines = []
        for i, (t, glow) in enumerate(ev):
            # sample just after the event so the caption/step at t is active
            page.evaluate(SET_STATE, [t + 0.01, glow])
            f = tmp / f"f{i:04d}.png"
            page.screenshot(path=str(f))
            end = ev[i + 1][0] if i + 1 < len(ev) else D["duration"]
            lines += [f"file '{f}'", f"duration {max(end - t, 0.04):.3f}"]
        lines.append(f"file '{tmp / f'f{len(ev) - 1:04d}.png'}'")
        (tmp / "list.txt").write_text("\n".join(lines) + "\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                        "-i", str(tmp / "audio.mp3"), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-tune", "stillimage",
                        "-crf", "22", "-preset", "medium", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
                        str(tmp / "out.mp4")], check=True)
        shutil.copyfile(tmp / "out.mp4", out_mp4)
    size = out_mp4.stat().st_size / 1e6
    print(f"ok: {out_mp4.name} · {D['duration']/60:.1f} min · {len(ev)} frames · {size:.1f} MB")


def main():
    out_dir = Path(sys.argv[1]); out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H})
        for h in sys.argv[2:]:
            h = Path(h)
            export(page, h, out_dir / (h.stem + ".mp4"))
        b.close()


if __name__ == "__main__":
    main()
