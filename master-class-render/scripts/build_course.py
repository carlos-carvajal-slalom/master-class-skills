#!/usr/bin/env python3
"""Build a master-class course: scripts + scenes -> MP4 videos + Obsidian notes (lesson notes + MOC).

Usage:
  build_course.py --source <dir with scripts/ and scenes/> --videos <dir> --notes <dir> --moc "<MOC title>"
                  [--course "<label shown on video>"] [--voice am_michael] [--lang en-us]
                  [--tags "a,b,c"] [--intro "MOC intro text"] [--only 01,03] [--notes-only]
"""
import argparse, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable


def run(cmd):
    r = subprocess.run(cmd, text=True, capture_output=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out)
    if r.returncode:
        raise SystemExit(f"failed: {' '.join(map(str, cmd[:3]))} …")
    return out


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--source", required=True); a.add_argument("--videos", required=True)
    a.add_argument("--notes", required=True); a.add_argument("--moc", required=True)
    a.add_argument("--course", default=""); a.add_argument("--voice", default="am_michael"); a.add_argument("--lang", default="en-us")
    a.add_argument("--tags", default="type/lesson"); a.add_argument("--intro", default="")
    a.add_argument("--only", default=""); a.add_argument("--notes-only", action="store_true")
    args = a.parse_args()

    src = Path(args.source)
    scripts = sorted((src / "scripts").glob("[0-9][0-9] - *.script.md"))
    only = {x.strip().zfill(2) for x in args.only.split(",") if x.strip()}
    if only:
        scripts = [s for s in scripts if s.name[:2] in only]
    if not scripts:
        raise SystemExit(f"no scripts found in {src / 'scripts'} (expected 'NN - Title.script.md')")

    if not args.notes_only:
        with tempfile.TemporaryDirectory() as tmp:
            htmls, warnings = [], 0
            for s in scripts:
                stem = s.name.removesuffix(".script.md")
                scenes = src / "scenes" / f"{stem[:2]}.scenes.md"
                if not scenes.exists():
                    raise SystemExit(f"missing scenes file: {scenes}")
                html = Path(tmp) / f"{stem}.html"
                out = run([PY, HERE / "render.py", s, scenes, html, "--course", args.course, "--voice", args.voice, "--lang", args.lang])
                warnings += out.count("warning:")
                htmls.append(html)
            if warnings:
                print(f"!! {warnings} @at phrase(s) not found; fix the scenes files (see warnings above)")
            run([PY, HERE / "export_mp4.py", args.videos, *htmls])

    run([PY, HERE / "make_notes.py", src / "scripts", src / "scenes", args.videos, args.notes, args.moc,
         "--tags", args.tags, "--intro", args.intro])


if __name__ == "__main__":
    main()
