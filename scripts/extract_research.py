#!/usr/bin/env python3
"""One-time extractor: research.qmd -> data/*.yml.

Run once to bootstrap the data files. After that data/ is the source of
truth and build_research.py regenerates research.qmd from it.
"""
import re, sys, unicodedata, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "research.qmd"

LINK = re.compile(r'\[([^\]]+)\]\((\S+?)\)')


def slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[\s_]+", "-", s)


def parse_authors(line, people):
    """'[with [A](u), B, and C]{.authors}' -> ordered list of person keys."""
    inner = re.match(r'\[with (.*)\]\{\.authors\}\\?$', line).group(1)
    # split on ", " and " and ", keeping link text intact
    parts = re.split(r',\s*and\s+|\s+and\s+|,\s+', inner)
    keys = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        m = LINK.fullmatch(p)
        name, url = (m.group(1), m.group(2)) if m else (p, None)
        k = slug(name)
        rec = people.setdefault(k, {"name": name})
        if url:
            rec["url"] = url
        keys.append(k)
    return keys


def parse_links(line):
    inner = re.match(r'\[(.*)\]\{\.paper-links\}$', line).group(1)
    out = []
    for chunk in inner.split(" · "):
        m = LINK.match(chunk.strip())
        if not m:
            raise ValueError("unparsed link chunk: %r" % chunk)
        rec = {"label": m.group(1), "url": m.group(2)}
        note = chunk.strip()[m.end():].strip()
        if note:
            rec["note"] = note
        out.append(rec)
    return out


def parse_outlet(line, section):
    """Parse '[...]{.outlet}' into structured fields."""
    s = re.match(r'\[(.*)\]\{\.outlet\}$', line).group(1)
    o = {}
    if s.startswith("Forthcoming, "):
        o["status"] = "forthcoming"
        o["outlet"] = re.fullmatch(r'Forthcoming, \*(.+)\*', s).group(1)
        return o
    o["status"] = "published"
    if section == "Book Chapters":
        m = re.fullmatch(r'In \*(.+?)\*(?:, pp\. (\S+))?, (\d{4})', s)
        o["outlet"], pages, year = m.group(1), m.group(2), m.group(3)
        if pages:
            o["pages"] = pages
        o["year"] = int(year)
        return o
    if not s.startswith("*"):                      # non-italic report
        m = re.fullmatch(r'(.+?), (\w+) (\d{4})', s)
        o["outlet"], o["month"], o["year"] = m.group(1), m.group(2), int(m.group(3))
        return o
    m = re.fullmatch(r'\*(.+?)\*, (.+), (\d{4})', s)
    o["outlet"] = m.group(1)
    o["year"] = int(m.group(3))
    cite = m.group(2)
    m2 = re.fullmatch(r'(\d+)\((\d+)\): (\S+)', cite)
    m3 = re.fullmatch(r'(\d+): (\S+)', cite)
    if m2:
        o["volume"], o["issue"], o["pages"] = int(m2.group(1)), int(m2.group(2)), m2.group(3)
    elif m3:
        o["volume"], o["pages"] = int(m3.group(1)), m3.group(2)
    else:
        o["pages"] = cite                          # bare article number
    return o


def main():
    # This is a ONE-TIME bootstrap. data/ is the source of truth now, and it
    # has been hand-edited; re-running would silently discard those edits.
    existing = [p.name for p in (ROOT / "data").glob("*.yml")]
    if existing and "--force" not in sys.argv:
        sys.exit("refusing to overwrite existing data/ files (%s).\n"
                 "This script is a one-time bootstrap; data/ is now the source of "
                 "truth. Pass --force only if you really mean to regenerate from "
                 "research.qmd and lose hand edits." % ", ".join(sorted(existing)))

    lines = SRC.read_text().split("\n")
    front = []
    i = 0
    if lines[0] == "---":
        j = lines.index("---", 1)
        front = lines[: j + 1]
        i = j + 1

    people, works, media, section = {}, [], None, None
    while i < len(lines):
        line = lines[i]
        if line.startswith("## ") and not line.startswith("## Abstract"):
            section = line[3:].strip()
        elif line == ":::: {.paper}":
            j = i + 1
            title = lines[j][4:].strip()
            j += 1
            w = {"section": section, "title": title}
            body_abs, callout_head = None, None
            while lines[j] != "::::":
                l = lines[j]
                if l.endswith("{.authors}") or l.endswith("{.authors}\\"):
                    w["authors"] = parse_authors(l, people)
                elif l.endswith("{.outlet}"):
                    w.update(parse_outlet(l, section))
                elif l.endswith("{.paper-links}"):
                    w["links"] = parse_links(l)
                elif l.startswith("::: {.callout-note"):
                    callout_head = lines[j + 1][3:].strip()
                    k = j + 2
                    body = []
                    while lines[k] != ":::":
                        body.append(lines[k])
                        k += 1
                    body_abs = "\n".join(body)
                    j = k
                elif l.startswith("- *"):
                    media = media or []
                    media.append(l[2:])
                j += 1
            if title == "Media coverage":
                pass                                # captured into `media`
            else:
                if callout_head:
                    w["abstract_heading"] = callout_head
                    w["abstract"] = body_abs
                if "status" not in w:
                    w["status"] = "working"
                works.append(w)
            i = j
        i += 1

    # assign stable ids: reuse the paper PDF's basename where Keaton already
    # chose one, otherwise build a readable slug from meaningful title words
    STOP = {"a", "an", "the", "of", "and", "in", "on", "for", "to", "from",
            "does", "do", "did", "are", "is", "with", "their", "its",
            "will", "through", "when", "have", "us"}
    seen = {}
    for w in works:
        base = None
        for l in w.get("links", []):
            m = re.fullmatch(r'assets/pdf/([\w-]+)\.pdf', l["url"])
            if m:
                base = m.group(1)
                break
        if not base:
            words = [x for x in slug(w["title"]).split("-") if x and x not in STOP]
            base = "-".join(words[:4])
        n = seen.get(base, 0) + 1
        seen[base] = n
        w["id"] = base if n == 1 else f"{base}-{n}"

    order = ["id", "title", "section", "status", "authors", "outlet",
             "volume", "issue", "pages", "month", "year", "links",
             "abstract_heading", "abstract"]
    works = [{k: w[k] for k in order if k in w} for w in works]

    out = ROOT / "data"
    yaml.SafeDumper.add_representer(
        str, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", v,
                                             style="|" if ("\n" in v or len(v) > 200) else None))
    (out / "works.yml").write_text(yaml.safe_dump(works, sort_keys=False,
                                                  allow_unicode=True, width=100000))
    (out / "people.yml").write_text(yaml.safe_dump(dict(sorted(people.items())),
                                                   sort_keys=False, allow_unicode=True, width=100000))
    (out / "media.yml").write_text(yaml.safe_dump(media, sort_keys=False,
                                                  allow_unicode=True, width=100000))
    (out / "_frontmatter.yml").write_text("\n".join(front) + "\n")
    print(f"works: {len(works)}  people: {len(people)}  media: {len(media)}")


if __name__ == "__main__":
    main()
