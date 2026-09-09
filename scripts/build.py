#!/usr/bin/env python3
"""Build every generated file on the site from data/.

Run it directly, or let Quarto run it (it is the project's pre-render step):

    python3 scripts/build.py          # regenerate + validate
    python3 scripts/build.py --check  # validate only; fail if a file is stale

data/ is the source of truth. research.qmd is a build product -- edits to it
are overwritten the next time this runs.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("error: PyYAML is not installed.  Fix with:  python3 -m pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SECTIONS = ["Journal Articles", "Book Chapters", "Working Papers", "Policy Reports & Media"]
STATUSES = {"working", "under-review", "forthcoming", "published"}
CALLOUT = '::: {.callout-note appearance="simple" collapse="true" icon="false"}'
BANNER = "# GENERATED FILE -- edit data/*.yml and run scripts/build.py instead."


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------
def validate(works, people, media):
    """Return a list of human-readable problems. Empty list means all good."""
    errs, warns = [], []

    selves = [k for k, v in people.items() if v.get("self")]
    if len(selves) != 1:
        errs.append(f"people.yml: expected exactly one entry with 'self: true', found {selves}")
    me = selves[0] if selves else None

    for k, v in sorted(people.items()):
        if not v.get("name"):
            errs.append(f"people.yml: {k!r} has no name")
        if v.get("needs_full_name"):
            warns.append(f"people.yml: {k!r} still has a placeholder name ({v.get('name')!r})")

    seen = {}
    for i, w in enumerate(works):
        where = f"works.yml[{i}] {w.get('id', '<no id>')!r}"
        for field in ("id", "title", "section", "status", "authors"):
            if not w.get(field):
                errs.append(f"{where}: missing {field!r}")
        if w.get("id") in seen:
            errs.append(f"{where}: duplicate id (also at index {seen[w['id']]})")
        seen[w.get("id")] = i
        if w.get("section") not in SECTIONS:
            errs.append(f"{where}: unknown section {w.get('section')!r}; expected one of {SECTIONS}")
        if w.get("status") not in STATUSES:
            errs.append(f"{where}: unknown status {w.get('status')!r}; expected one of {sorted(STATUSES)}")
        for a in w.get("authors", []):
            if a not in people:
                errs.append(f"{where}: unknown author {a!r} — add it to data/people.yml")
        if me and me not in w.get("authors", []):
            warns.append(f"{where}: author list does not include {me!r}")
        if w.get("status") == "published" and not w.get("year"):
            errs.append(f"{where}: published work needs a year")
        if w.get("status") in ("published", "forthcoming") and not w.get("outlet"):
            errs.append(f"{where}: {w['status']} work needs an outlet")
        for l in w.get("links", []):
            if not l.get("label") or not l.get("url"):
                errs.append(f"{where}: every link needs a label and a url")
                continue
            u = l["url"]
            if not u.startswith(("http://", "https://")) and not (ROOT / u).exists():
                errs.append(f"{where}: link {l['label']!r} points at {u}, which does not exist")

    ids = {w.get("id") for w in works}
    for i, m in enumerate(media):
        where = f"media.yml[{i}]"
        for field in ("outlet", "month", "year", "title", "url"):
            if not m.get(field):
                errs.append(f"{where}: missing {field!r}")
        if m.get("work") and m["work"] not in ids:
            errs.append(f"{where}: work {m['work']!r} is not an id in works.yml")

    for w in warns:
        print(f"warning: {w}", file=sys.stderr)
    return errs


# --------------------------------------------------------------------------
# research.qmd
# --------------------------------------------------------------------------
def person(people, key):
    p = people[key]
    return f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]


def author_line(people, keys):
    # Full author list in the paper's own order, including Keaton. Solo-authored
    # work gets no line: naming yourself alone on your own site is noise.
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
    if w["status"] in ("working", "under-review"):
        return None
    if w["status"] == "forthcoming":
        return f"[Forthcoming, *{w['outlet']}*]{{.outlet}}"
    if w["section"] == "Book Chapters":
        pp = f", pp. {w['pages']}" if w.get("pages") else ""
        return f"[In *{w['outlet']}*{pp}, {w['year']}]{{.outlet}}"
    if w.get("number"):                                   # numbered report series
        when = f"{w['month']} {w['year']}" if w.get("month") else str(w["year"])
        return f"[{w['outlet']} No. {w['number']}, {when}]{{.outlet}}"
    if w.get("month"):                                    # non-italic report
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
    a, o = author_line(people, w["authors"]), outlet_line(w)
    if a:
        out.append(a + ("\\" if o else ""))     # line break only when an outlet follows
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
    return out + ["::::", ""]


def render_research(works, people, media, front):
    lines = list(front)
    lines.insert(len(lines) - 1, BANNER)        # inside the front matter, so it never renders
    lines.append("")
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
    return "\n".join(lines).rstrip("\n") + "\n"


# --------------------------------------------------------------------------
def main():
    check_only = "--check" in sys.argv
    works  = yaml.safe_load((DATA / "works.yml").read_text())
    people = yaml.safe_load((DATA / "people.yml").read_text())
    media  = yaml.safe_load((DATA / "media.yml").read_text())
    front  = (DATA / "_frontmatter.yml").read_text().rstrip("\n").split("\n")

    errs = validate(works, people, media)
    if errs:
        print(f"\n{len(errs)} problem(s) found in data/:\n", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    targets = {ROOT / "research.qmd": render_research(works, people, media, front)}

    stale = [p for p, text in targets.items()
             if not p.exists() or p.read_text() != text]
    if check_only:
        if stale:
            print("stale (run scripts/build.py): " +
                  ", ".join(p.name for p in stale), file=sys.stderr)
            sys.exit(1)
        print(f"up to date: {len(targets)} file(s), {len(works)} works")
        return
    for p, text in targets.items():
        p.write_text(text)
    print(f"built {len(targets)} file(s) from {len(works)} works, "
          f"{len(people)} people, {len(media)} media items"
          + (f" — updated: {', '.join(p.name for p in stale)}" if stale else " — no changes"))


if __name__ == "__main__":
    main()
