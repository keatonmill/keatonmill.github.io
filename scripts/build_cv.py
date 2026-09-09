#!/usr/bin/env python3
"""Build the CV from data/ into assets/pdf/Keaton-Miller-CV.pdf.

    python3 scripts/build_cv.py            # build the PDF
    python3 scripts/build_cv.py --check    # non-zero if the PDF is stale

Publications come from data/works.yml and data/people.yml -- the same files
that drive the research page -- so a paper's authors, outlet and citation are
described in exactly one place. Everything the website has no equivalent for
(positions, education, grants, presentations, service, teaching, advising)
lives in data/cv.yml.

This script normalises all of that into scripts/cv/content.json and then runs
Typst over scripts/cv/cv.typ, which does the typesetting. The JSON is an
intermediate, not a source file; it is gitignored.

Unlike scripts/build.py this is NOT a Quarto pre-render step. It needs Typst,
and its output is a committed binary, so it runs when the CV changes and not
on every site render.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CVDIR = os.path.join(ROOT, "scripts", "cv")
CONTENT = os.path.join(CVDIR, "content.json")
TEMPLATE = os.path.join(CVDIR, "cv.typ")
OUT = os.path.join(ROOT, "assets", "pdf", "Keaton-Miller-CV.pdf")

SELF = "miller"
ACCENT = "slate"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
SHORT = {m: m[:3] for m in MONTHS}

# Which works.yml section feeds which CV heading. Anything in works.yml whose
# section is not listed here simply does not reach the CV.
SECTION_OF = {
    "Journal Articles": "journals",
    "Book Chapters": "chapters",
    "Working Papers": "working",
    "Policy Reports & Media": "other",
}


def load(path):
    with open(path) as f:
        return yaml.safe_load(f)


# --------------------------------------------------------------------------
# validation


def validate(works, people, cv):
    """Fail loudly and write nothing, the way scripts/build.py does."""
    errs = []

    for key in ("meta", "positions", "education", "grants", "presentations",
                "referee", "grant_review", "dept_service", "univ_service",
                "teaching", "advising"):
        if not cv.get(key):
            errs.append(f"cv.yml: missing or empty {key!r}")
    for key in ("name", "role", "email", "website", "website_url", "address"):
        if not (cv.get("meta") or {}).get(key):
            errs.append(f"cv.yml: meta is missing {key!r}")
    for key in ("current", "past", "undergraduate"):
        if not (cv.get("advising") or {}).get(key):
            errs.append(f"cv.yml: advising is missing {key!r}")
    if not (cv.get("referee") or {}).get("journals"):
        errs.append("cv.yml: referee.journals is missing or empty")
    for i, a in enumerate((cv.get("referee") or {}).get("assignments") or []):
        if not a.get("journal") or not a.get("date"):
            errs.append(f"cv.yml: referee.assignments[{i}] needs a journal and a date")
        if a.get("kind") not in (None, "sign-off"):
            errs.append(f"cv.yml: referee.assignments[{i}] has kind {a['kind']!r}; "
                        f"expected 'sign-off', or nothing for a written report")
    for i, p in enumerate(cv.get("presentations") or []):
        for item in p.get("items") or []:
            if isinstance(item, dict) and item.get("kind") not in KINDS:
                errs.append(f"cv.yml: presentation {item.get('name')!r} has kind "
                            f"{item.get('kind')!r}; expected one of {sorted(KINDS)}")
    for i, t in enumerate(cv.get("teaching") or []):
        for key in ("course", "level", "count"):
            if t.get(key) in (None, ""):
                errs.append(f"cv.yml: teaching[{i}] is missing {key!r}")
        if t.get("count") is not None and len(t.get("offerings") or []) > t["count"]:
            errs.append(f"cv.yml: teaching[{i}] lists more offerings than its count")
        for term in t.get("offerings") or []:
            if not is_term(term):
                errs.append(f"cv.yml: teaching[{i}] offering {term!r} is not a "
                            f"term like 'Fall 2023'")
    # `completed` is a term, not a year: a review period is an arbitrary pair
    # of dates and routinely splits an academic year.
    for key in ("past", "undergraduate"):
        for i, s_ in enumerate((cv.get("advising") or {}).get(key) or []):
            done = s_.get("completed")
            if done and not is_term(done):
                errs.append(f"cv.yml: advising.{key}[{i}] completed {done!r} is "
                            f"not a term like 'Spring 2026'")

    if SELF not in people:
        errs.append(f"people.yml: no {SELF!r} entry, so no name can be bolded")

    for i, w in enumerate(works):
        if w.get("section") not in SECTION_OF:
            continue
        where = f"works.yml[{i}] {w.get('id')!r}"
        for a in w.get("authors", []):
            if a not in people:
                errs.append(f"{where}: unknown author {a!r}")
            elif not people[a].get("cite"):
                errs.append(f"{where}: author {a!r} has no 'cite:' form, which "
                            f"the CV needs")
        if w["section"] == "Working Papers" and draft_of(w) is None:
            errs.append(f"{where}: working paper has no draft date — add "
                        f"'draft: <Month Year>', or a 'Paper' link with a "
                        f"'note: (Month Year)'")
        if w["section"] == "Working Papers":
            d = draft_of(w)
            if d and d.split()[0] not in SHORT.values():
                errs.append(f"{where}: draft date {d!r} is not '<Month Year>'")
    return errs


# --------------------------------------------------------------------------
# shaping


def cite_list(people, keys):
    """[(cite form, is Keaton), ...] in the paper's own author order."""
    return [[people[k]["cite"], k == SELF] for k in keys]


def draft_of(w):
    """Date of a working paper's last draft.

    An explicit `draft:` wins. Otherwise it comes from the note on the Paper
    link, which is where the research page already records it. The month is
    abbreviated to keep the CV's date column narrow.
    """
    raw = w.get("draft")
    if raw is None:
        for l in (w.get("links") or []):
            if l.get("label") == "Paper" and l.get("note"):
                raw = l["note"].strip("()")
                break
    if raw is None:
        return None
    parts = raw.split()
    if len(parts) != 2 or parts[0] not in SHORT:
        return raw
    return f"{SHORT[parts[0]]} {parts[1]}"


def draft_key(entry):
    """Newest draft first; anything undated sorts last."""
    d = entry.get("draft")
    if not d:
        return (0, 0)
    month, year = d.split()
    order = list(SHORT.values()).index(month) + 1
    return (int(year), order)


def detail_of(w):
    """The citation tail: volume(issue): pages, or a report's series number."""
    if w.get("number"):
        return f"No. {w['number']}"
    vol, iss, pages = w.get("volume"), w.get("issue"), w.get("pages")
    if vol and iss and pages:
        return f"{vol}({iss}): {pages}"
    if vol and pages:
        return f"{vol}: {pages}"
    return str(pages) if pages else ""


def url_of(w):
    """The publisher page. Links to files inside the repo are not that."""
    links = w.get("links") or []
    for want in ("Published version", "Report"):
        for l in links:
            if l.get("label") == want and l["url"].startswith("http"):
                return l["url"]
    for l in links:
        if l["url"].startswith("http"):
            return l["url"]
    return None


def entry(w, people, kind):
    e = {
        "id": w["id"],
        "authors": cite_list(people, w.get("authors", [])),
        "year": w.get("year"),
        "title": w["title"],
        "outlet": w.get("outlet"),
        "url": url_of(w),
        "detail": "" if w["status"] == "forthcoming" else detail_of(w),
        "forthcoming": w["status"] == "forthcoming",
    }
    if kind == "chapters":
        bits = [b for b in (f"(ed. {w['editors']})" if w.get("editors") else None,
                            f"pp. {w['pages']}" if w.get("pages") else None) if b]
        e["detail"] = ", ".join(bits)
        e["prefix"] = "in "
    if kind == "working":
        e["draft"] = draft_of(w)
    return e


KINDS = {"conference", "invited", "public"}


def venue(item):
    if isinstance(item, str):
        return item
    return f"{item['name']} ({item['note']})" if item.get("note") else item["name"]


def cv_sections(cv):
    """Flatten cv.yml's dated records into the flat strings the CV prints.

    The data carries more than the CV shows -- referee assignment dates,
    teaching terms, when a student finished -- because a review-period report
    needs them and the CV does not.
    """
    ref = cv["referee"]
    journals = sorted(set(ref["journals"])
                      | {a["journal"] for a in (ref.get("assignments") or [])})

    def note(t):
        bits = [f"x{t['count']}", t["level"]]
        if t.get("enrollment"):                 # not recorded for every course
            bits.append(f"typical enrollment {t['enrollment']}")
        return ", ".join(bits)

    teaching = [{"course": t["course"], "note": note(t)} for t in cv["teaching"]]

    adv = cv["advising"]
    past = [f"{s['name']} ({s['role']}) – {s['placement']}" for s in adv["past"]]
    current = [f"{s['name']} ({s['stage']}) – {s['status']}" for s in adv["current"]]
    under = [f"{s['name']} – {s['what']} ({s['role']})" for s in adv["undergraduate"]]

    return {
        "referee": journals,
        "teaching": teaching,
        "advising": {"current": current, "past": past, "undergraduate": under},
        # the CV prints the venue and any annotation; `kind` is for reports
        "presentations": [{"year": p["year"],
                           "items": [venue(i) for i in p["items"]]}
                          for p in cv["presentations"]],
    }


def build_content(works, people, cv):
    buckets = {name: [] for name in SECTION_OF.values()}
    for w in works:
        kind = SECTION_OF.get(w.get("section"))
        if kind:
            buckets[kind].append(entry(w, people, kind))

    buckets["working"].sort(key=draft_key, reverse=True)
    buckets["other"].sort(key=lambda e: -(e["year"] or 9999))

    content = {k: cv[k] for k in
               ("meta", "grants", "grant_review", "dept_service",
                "univ_service", "positions", "education")}
    content.update(cv_sections(cv))
    content.update(buckets)
    return content


# --------------------------------------------------------------------------
# main


TERM_MONTH = {"Winter": 1, "Spring": 4, "Summer": 7, "Fall": 10}


def term_date(term):
    """'Fall 2023' -> the date its instruction roughly starts."""
    name, year = str(term).split()
    return datetime.date(int(year), TERM_MONTH[name], 1)


def is_term(term):
    """True if `term` parses as 'Season Year'."""
    try:
        term_date(term)
    except (ValueError, KeyError):
        return False
    return True


def span(years):
    """'2023-2024' or '2024-present' -> (first year, last year or None)."""
    parts = re.split(r"[–-]", str(years))
    first = int(parts[0])
    if len(parts) == 1:
        return first, first
    return first, None if not parts[1].strip().isdigit() else int(parts[1])


def coverage(works, cv, since, until):
    """What is dated, what is not, and what falls inside a review window."""
    print(f"Review window: {since} to {until}\n")

    pubs = [w for w in works if w.get("section") in
            ("Journal Articles", "Book Chapters", "Policy Reports & Media")]
    dated = [w for w in pubs if w.get("accepted")]
    inwin = [w for w in dated if since <= w["accepted"] <= until]
    print(f"Publications          {len(dated)}/{len(pubs)} have an acceptance date"
          f"  -> {len(inwin)} accepted in window")
    for w in pubs:
        if not w.get("accepted"):
            print(f"    no acceptance date: {w['title'][:62]}")

    wps = [w for w in works if w.get("section") == "Working Papers"]
    print(f"Working papers        {sum(1 for w in wps if draft_of(w))}/{len(wps)} "
          f"have a draft date")

    ref = cv["referee"]
    asg = ref.get("assignments") or []
    # A sign-off is a revision Keaton read and was satisfied by, so no report
    # was written. It is service either way, but a merit form that asks for
    # reports is asking for the other number -- so never merge the two.
    reports = [a for a in asg if a.get("kind") != "sign-off"]
    signoffs = [a for a in asg if a.get("kind") == "sign-off"]
    inwin = [a for a in reports if since <= a["date"] <= until]
    print(f"Referee reports       {len(reports)} written"
          f"  -> {len(inwin)} in window")
    if signoffs:
        sw = [a for a in signoffs if since <= a["date"] <= until]
        print(f"    plus {len(signoffs)} revision sign-offs, read but not "
              f"written up  -> {len(sw)} in window")
    if asg:
        print(f"    {len(asg)} assignments in all, across "
              f"{len({a['journal'] for a in asg})} journals")
    else:
        print(f"    nothing logged yet; the CV still lists all "
              f"{len(ref['journals'])} journals")

    tot = sum(t["count"] for t in cv["teaching"])
    rec = sum(len(t.get("offerings") or []) for t in cv["teaching"])
    print(f"Teaching              {rec}/{tot} offerings have a term recorded")
    for t in cv["teaching"]:
        off = [o for o in (t.get("offerings") or [])
               if since <= term_date(o) <= until]
        gap = t["count"] - len(t.get("offerings") or [])
        note = f", {gap} undated" if gap else ""
        print(f"    {len(off)} in window  {t['course'][:52]}{note}")

    past = cv["advising"]["past"]
    done = [s for s in past if s.get("completed")]
    inwin = [s for s in done if since <= term_date(s["completed"]) <= until]
    print(f"Graduate advising     {len(done)}/{len(past)} past students have a "
          f"completion term  -> {len(inwin)} in window")

    pres = [(p["year"], i) for p in cv["presentations"] for i in p["items"]]
    kinds = sum(1 for _, i in pres if isinstance(i, dict) and i.get("kind"))
    inwin = [y for y, _ in pres if since.year <= int(y) <= until.year]
    print(f"Presentations         {kinds}/{len(pres)} say whether they were a "
          f"conference or an invited seminar  -> {len(inwin)} in window (by year)")

    print("\nYear-granularity sections (presentations, service, grants) can only "
          "\nbe matched to a window by year, so a window that starts mid-year "
          "\nover-counts. Acceptance dates, referee dates and teaching terms "
          "\nare exact.")


def text_of(path):
    return subprocess.run(["pdftotext", "-nopgbrk", path, "-"],
                          capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="rebuild to a temporary file and fail if the "
                         "committed PDF's text differs")
    ap.add_argument("--coverage", action="store_true",
                    help="report which records carry dates, and how many fall "
                         "inside a review window")
    ap.add_argument("--since", default="2023-09-16", help="window start (ISO)")
    ap.add_argument("--until", default="2026-03-20", help="window end (ISO)")
    args = ap.parse_args()

    works = load(os.path.join(ROOT, "data", "works.yml"))
    people = load(os.path.join(ROOT, "data", "people.yml"))
    cv = load(os.path.join(ROOT, "data", "cv.yml"))

    if args.coverage:
        coverage(works, cv,
                 datetime.date.fromisoformat(args.since),
                 datetime.date.fromisoformat(args.until))
        return

    errs = validate(works, people, cv)
    if errs:
        for e in errs:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if not shutil.which("typst"):
        sys.exit("error: typst is not installed — `brew install typst`")

    content = build_content(works, people, cv)
    os.makedirs(CVDIR, exist_ok=True)
    with open(CONTENT, "w") as f:
        json.dump(content, f, indent=1, ensure_ascii=False)

    tmp = tempfile.mkdtemp()
    target = os.path.join(tmp, "check.pdf") if args.check else OUT
    cmd = ["typst", "compile", "--root", ROOT,
           "--input", f"accent={ACCENT}", TEMPLATE, target]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit("error: typst failed")
    for line in r.stderr.splitlines():
        if line.strip():
            print(line, file=sys.stderr)

    n = sum(len(content[k]) for k in ("journals", "chapters", "working", "other"))
    if args.check:
        # Typst stamps a build time, so two builds of identical data are not
        # byte-identical. Compare what is actually on the page instead.
        if not shutil.which("pdftotext"):
            shutil.rmtree(tmp, ignore_errors=True)
            sys.exit("error: --check needs pdftotext (brew install poppler)")
        if not os.path.exists(OUT):
            shutil.rmtree(tmp, ignore_errors=True)
            sys.exit(f"error: {os.path.relpath(OUT, ROOT)} does not exist")
        fresh, committed = (text_of(target), text_of(OUT))
        shutil.rmtree(tmp, ignore_errors=True)
        if fresh != committed:
            sys.exit(f"error: {os.path.relpath(OUT, ROOT)} is stale — "
                     f"run python3 scripts/build_cv.py")
        print(f"CV is up to date ({n} works)")
    else:
        print(f"wrote {os.path.relpath(OUT, ROOT)} from {n} works "
              f"+ data/cv.yml")


if __name__ == "__main__":
    main()
