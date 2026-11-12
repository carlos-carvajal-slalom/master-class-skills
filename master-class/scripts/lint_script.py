#!/usr/bin/env python3
"""Mechanical rubric check for master-class lesson scripts.

Usage: lint_script.py <scripts_dir or file.script.md ...> [--sources <file or dir> ...]
Exit 1 if any lesson has errors. Fix every ERROR; read every WARN and fix it unless it is clearly intended.
"""
import argparse, re, sys
from pathlib import Path

DEFINITION_OPEN = re.compile(r"^(An? |The )?[A-Z][\w\-() ]{0,40}? (is|are) (an?|the) |^[\w\-() ]{1,40} (refers to|means|stands for) ")
LIST_LINE = re.compile(r"^\s*([-*•]\s|[|#>]|\d+[.)]\s)")


def beats_of(text):
    out = []
    for m in re.finditer(r"^### Beat (\d+) · (.+?)\n(.*?)(?=^### Beat |\Z)", text, re.S | re.M):
        body = m.group(3)
        narr = re.search(r"\*\*Narration:\*\*\n(.*)", body, re.S)
        lines = [l for l in (narr.group(1) if narr else "").strip().split("\n") if l.strip()]
        out.append({"n": int(m.group(1)), "title": m.group(2).strip(), "has_screen": "**Screen:**" in body,
                    "has_narr": bool(narr), "lines": lines})
    return out


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?…])\s+|(?<=[.!?…][\"”’])\s+", text) if s and s.strip()]


def lint(path, first, last, source_text):
    t = path.read_text()
    E, W = [], []
    if not re.search(r"^# \d+ · .+", t, re.M):
        E.append("missing title line '# NN · Title'")
    for k in ("Goal", "Misconception"):
        if not re.search(rf"^\*\*{k}:\*\* .+", t, re.M):
            E.append(f"missing **{k}:** line")
    beats = beats_of(t)
    if len(beats) < 6:
        E.append(f"only {len(beats)} beats (need ≥ 6)")
    for b in beats:
        if not b["has_screen"]:
            E.append(f"beat {b['n']}: missing **Screen:**")
        if not b["has_narr"] or not b["lines"]:
            E.append(f"beat {b['n']}: missing **Narration:**")
        for l in b["lines"]:
            if LIST_LINE.match(l):
                E.append(f"beat {b['n']}: narration contains a list/table/heading line: {l[:50]!r}")
            if re.search(r"https?://", l):
                E.append(f"beat {b['n']}: URL in narration (not speakable)")
            for s in sentences(l):
                n = len(s.split())
                if n > 38:
                    W.append(f"beat {b['n']}: {n}-word sentence (split it): {s[:60]!r}…")
    titles = [b["title"].lower() for b in beats]
    if beats and "hook" not in titles[0]:
        E.append("beat 1 must be the Hook (title starts with 'Hook')")
    if beats and beats[0]["lines"]:
        first_sentence = sentences(beats[0]["lines"][0])[0]
        if DEFINITION_OPEN.match(re.sub(r"[*`]", "", first_sentence)):
            W.append(f"beat 1 may open with a definition: {first_sentence[:70]!r} (open with a scene/problem)")
    rp = [b for b in beats if "retrieval" in b["title"].lower()]
    if not rp:
        E.append("no 'Retrieval pause' beat")
    else:
        txt = " ".join(rp[0]["lines"])
        if not first and "…" not in txt:
            E.append("Retrieval pause narration needs '…' between the question and the answer")
        elif "…" in txt and not txt.split("…", 1)[1].strip():
            E.append("Retrieval pause has no answer after '…'")
    if not first and not last and not any("limit" in x for x in titles):
        E.append("no Limits beat (title containing 'Limits')")
    if not last and beats and not re.search(r"bridge", titles[-1]):
        E.append("last beat must be a bridge to the next lesson (title contains 'bridge')")
    words = sum(len(l.split()) for b in beats for l in b["lines"])
    if words < 350:
        W.append(f"only {words} narrated words (~{words/150:.1f} min): probably too shallow")
    if words > 1150:
        W.append(f"{words} narrated words (~{words/150:.1f} min): one goal per lesson; consider splitting")
    if source_text:
        narr = " ".join(l for b in beats for l in b["lines"])
        for num in sorted(set(re.findall(r"(?<![\w-])\$?\d[\d,.]*\d%?|\b\d{2,}\b", narr))):
            core = num.strip("$%").replace(",", "")
            if core and core not in source_text.replace(",", ""):
                W.append(f"number {num} not found in the sources: verify it is not invented")
    return words, E, W


def main():
    a = argparse.ArgumentParser()
    a.add_argument("paths", nargs="+"); a.add_argument("--sources", nargs="*", default=[])
    args = a.parse_args()
    files = []
    for p in map(Path, args.paths):
        files += sorted(p.glob("[0-9][0-9] - *.script.md")) if p.is_dir() else [p]
    if not files:
        sys.exit("no '*.script.md' files found")
    src = ""
    for s in map(Path, args.sources):
        for f in ([s] if s.is_file() else [*s.rglob("*.md"), *s.rglob("*.ipynb"), *s.rglob("*.py")]):
            try:
                src += f.read_text(errors="ignore") + "\n"
            except OSError:
                pass
    nums = sorted(int(f.name[:2]) for f in files)
    bad, total = 0, 0
    for f in files:
        n = int(f.name[:2])
        words, E, W = lint(f, n == 0, n == nums[-1] and len(nums) > 1, src)
        total += words
        status = "FAIL" if E else ("WARN" if W else "PASS")
        bad += bool(E)
        print(f"{status}  {f.name}  ({words} words, ~{words/150:.1f} min)")
        for e in E:
            print(f"   ERROR {e}")
        for w in W:
            print(f"   WARN  {w}")
    print(f"\n{len(files) - bad}/{len(files)} lessons without errors · ~{total/150:.0f} min total")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
