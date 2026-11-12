#!/usr/bin/env python3
"""Generate Obsidian notes (one per lesson + a MOC) that embed the lesson MP4s.

Usage: make_notes.py <scripts_dir> <scenes_dir> <videos_dir> <notes_dir> "<MOC title>" [--tags a,b] [--intro "text"]
"""
import argparse, re, subprocess
from pathlib import Path


def clean(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", s)
    return s.strip()


def duration(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def mmss(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def parse(script):
    t = script.read_text()
    title = re.search(r"^# \d+ · (.+)$", t, re.M).group(1).strip()
    field = lambda k: (re.search(rf"^\*\*{k}:\*\* (.+)$", t, re.M) or [None, ""])[1]
    beats = []
    for m in re.finditer(r"^### Beat (\d+) · (.+?)\n(.*?)(?=^### Beat |\Z)", t, re.S | re.M):
        body = m.group(3)
        screen = (re.search(r"\*\*Screen:\*\*(.*?)(?=\*\*Narration:\*\*)", body, re.S) or [None, ""])[1]
        narr = (re.search(r"\*\*Narration:\*\*\n(.*)", body, re.S) or [None, ""])[1]
        paras = [p.strip() for p in narr.strip().split("\n") if p.strip()]
        beats.append({"n": int(m.group(1)), "title": m.group(2).strip(), "screen": screen, "paras": paras})
    return {"title": title, "goal": clean(field("Goal")), "misc": clean(field("Misconception")), "beats": beats}


def key_ideas(scenes_file, retrieval_beats):
    if not scenes_file.exists():
        return []
    ideas = []
    for m in re.finditer(r"^## Beat (\d+)\s*\n```d2\n(.*?)```", scenes_file.read_text(), re.S | re.M):
        if int(m.group(1)) in retrieval_beats:
            continue
        for lab in re.findall(r'^\s*[\w.]+:\s*"(.+?)"\s*\{[^}\n]*class:\s*note', m.group(2), re.M):
            idea = re.sub(r"\s+", " ", lab.replace("\\n", " ").replace('\\"', '"').replace("\\$", "$")).strip().lstrip("…").strip()
            if idea.endswith("?") or idea in ideas:
                continue
            ideas.append(idea)
    return ideas


def check_yourself(lesson):
    for b in lesson["beats"]:
        if "retrieval" not in b["title"].lower():
            continue
        q = re.match(r'\s*\*"(.+?)"\*\s*$', b["screen"].strip().split("\n")[0])
        text = " ".join(b["paras"])
        before, _, after = text.partition("…")
        question = clean(q.group(1)) if q else clean(before)
        return b["n"], question, clean(after) if after else ""
    return None, "", ""


def callout(kind, title, lines, fold=""):
    out = [f"> [!{kind}]{fold} {title}".rstrip()]
    for ln in lines:
        out.append(f"> {ln}" if ln else ">")
    return "\n".join(out)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("scripts"); a.add_argument("scenes"); a.add_argument("videos"); a.add_argument("notes"); a.add_argument("moc")
    a.add_argument("--tags", default="type/lesson"); a.add_argument("--intro", default="")
    args = a.parse_args()
    scripts, scenes, videos, notes = map(Path, (args.scripts, args.scenes, args.videos, args.notes))
    notes.mkdir(parents=True, exist_ok=True)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    files = sorted(scripts.glob("[0-9][0-9] - *.md"))
    lessons = []
    for f in files:
        L = parse(f)
        stem = f.stem.removesuffix(".script")
        L["stem"], L["num"] = stem, stem[:2]
        mp4 = videos / f"{stem}.mp4"
        L["mp4"], L["dur"] = mp4.name, duration(mp4) if mp4.exists() else 0
        lessons.append(L)

    for i, L in enumerate(lessons):
        rb, question, answer = check_yourself(L)
        ideas = key_ideas(scenes / f"{L['num']}.scenes.md", {rb} if rb else set())
        prev_l = f"← [[{lessons[i - 1]['stem']}|{lessons[i - 1]['title']}]]" if i else ""
        next_l = f"[[{lessons[i + 1]['stem']}|{lessons[i + 1]['title']}]] →" if i + 1 < len(lessons) else ""
        nav = " · ".join(x for x in (prev_l, f"[[{args.moc}|Course index]]", next_l) if x)
        fm = ["---", "tags:", *[f"  - {t}" for t in tags], f"lesson: {int(L['num'])}", f'duration: "{mmss(L["dur"])}"',
              f'course: "[[{args.moc}]]"', "---"]
        body = [*fm, f"# {L['num']} · {L['title']}", "", f"![[{L['mp4']}]]", "",
                callout("abstract", "Goal", [L["goal"][:1].upper() + L["goal"][1:]]), ""]
        if L["misc"]:
            body += [f"**Misconception it takes apart:** {L['misc']}", ""]
        if ideas:
            body += ["## Key ideas", *[f"- {x}" for x in ideas], ""]
        if question:
            body += ["## Check yourself", callout("question", "Before you open the answer", [question])]
            if answer:
                body += ["", callout("success", "Answer", [answer], "-")]
            body += [""]
        tr = []
        for b in L["beats"]:
            tr += [f"**{b['n']} · {b['title']}**", *[x for p in b["paras"] for x in (clean(p), "")]]
        body += ["## Transcript", callout("quote", "Transcript", tr[:-1] if tr and tr[-1] == "" else tr, "-"), "", "---", nav, ""]
        (notes / f"{L['stem']}.md").write_text("\n".join(body))

    total = sum(L["dur"] for L in lessons)
    rows = [f"| {L['num']} | [[{L['stem']}\\|{L['title']}]] | {mmss(L['dur'])} | {L['misc'].replace(chr(34), '').replace('|', '/')} |" for L in lessons]
    moc = ["---", "tags:", *[f"  - {t}" for t in tags if t != "type/lesson"], "  - type/moc", "---", f"# {args.moc}", ""]
    if args.intro:
        moc += [args.intro, ""]
    moc += [f"**{len(lessons)} lessons · {int(total // 60)} min.** Start with [[{lessons[0]['stem']}|{lessons[0]['title']}]].", "",
            "| # | Lesson | Length | Misconception it takes apart |", "|---|---|---|---|", *rows, ""]
    (notes / f"{args.moc}.md").write_text("\n".join(moc))
    print(f"notes: {len(lessons)} lessons + MOC · {total/60:.1f} min → {notes}")


if __name__ == "__main__":
    main()
