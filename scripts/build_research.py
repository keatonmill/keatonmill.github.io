#!/usr/bin/env python3
"""Generate research.qmd from data/*.yml.

data/ is the source of truth. Run this after editing it; research.qmd is a
build product and should not be hand-edited.
"""
import sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "research.qmd"

SECTIONS = ["Journal Articles", "Book Chapters", "Working Papers", "Policy Reports & Media"]
CALLOUT = '::: {.callout-note appearance="simple" collapse="true" icon="false"}'


def person(people, key):
    p = people.get(key)
    if p is None:
        sys.exit(f"error: unknown author key {key!r} — add it to data/people.yml")
    return f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]


def author_line(people, keys):
    # Full author list, in the paper's own order, including Keaton. Solo-authored
    # work gets no line at all -- naming yourself alone on your own site is noise.
    if all(people.get(k, {}).get("self") for k in keys):
        return None
    names = [person(people, k) for k in keys]
    if len(names) == 1:
        joined = names[0]
    elif len(names) == 2:
        joined = f"{names[0]} and {names[1]}"
    else:
        joined = ", ".join(names[:-1]) + f", and {names[-1]}"
    return f"[{joined}]{{.authors}}"


def outlet_line(w):
    """Inverse of extract_research.parse_outlet."""
    if w["status"] == "working":
        return None
    if w["status"] == "forthcoming":
        return f"[Forthcoming, *{w['outlet']}*]{{.outlet}}"
    if w["section"] == "Book Chapters":
        pp = f", pp. {w['pages']}" if w.get("pages") else ""
        return f"[In *{w['outlet']}*{pp}, {w['year']}]{{.outlet}}"
    if w.get("month"):                                   # non-italic report
        return f"[{w['outlet']}, {w['month']} {w['year']}]{{.outlet}}"
    if w.get("volume") and w.get("issue"):
        cite = f"{w['volume']}({w['issue']}): {w['pages']}"
    elif w.get("volume"):
        cite = f"{w['volume']}: {w['pages']}"
    else:
        cite = w["pages"]
    return f"[*{w['outlet']}*, {cite}, {w['year']}]{{.outlet}}"


def links_line(w):
    if not w.get("links"):
        return None
    parts = []
    for l in w["links"]:
        s = f"[{l['label']}]({l['url']})"
        if l.get("note"):
            s += f" {l['note']}"
        parts.append(s)
    return "[" + " · ".join(parts) + "]{.paper-links}"


def render_work(w, people):
    out = [":::: {.paper}", f"### {w['title']}", ""]
    a = author_line(people, w["authors"]) if w.get("authors") else None
    o = outlet_line(w)
    if a:
        out.append(a + ("\\" if o else ""))       # line break only when an outlet follows
    if o:
        out.append(o)
    if a or o:
        out.append("")
    ll = links_line(w)
    if ll:
        out += [ll, ""]
    if w.get("abstract"):
        out += [CALLOUT, f"## {w.get('abstract_heading', 'Abstract')}"]
        out += w["abstract"].split("\n")
        out += [":::"]
    out += ["::::", ""]
    return out


def main():
    works = yaml.safe_load((DATA / "works.yml").read_text())
    people = yaml.safe_load((DATA / "people.yml").read_text())
    media = yaml.safe_load((DATA / "media.yml").read_text())
    front = (DATA / "_frontmatter.yml").read_text().rstrip("\n").split("\n")

    for k, v in people.items():
        if v.get("needs_full_name"):
            print(f"warning: {k!r} has a placeholder name ({v['name']!r}) — "
                  f"set the real name in data/people.yml", file=sys.stderr)

    lines = front + [""]
    for sec in SECTIONS:
        items = [w for w in works if w["section"] == sec]
        if not items and sec != "Policy Reports & Media":
            continue
        lines += [f"## {sec}", ""]
        for w in items:
            lines += render_work(w, people)
        if sec == "Policy Reports & Media" and media:
            lines += [":::: {.paper}", "### Media coverage", ""]
            for m in media:
                s = f"*{m['outlet']}*, {m['month']} {m['year']}: [{m['title']}]({m['url']})"
                if m.get("note"):
                    s += f", {m['note']}"
                lines.append(f"- {s}")
            lines += ["::::"]

    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text)
    else:
        OUT.write_text(text)


if __name__ == "__main__":
    main()
