# Editing the research page and the CV

Both are **generated** from these files. `research.qmd` and
`assets/pdf/Keaton-Miller-CV.pdf` are build products; edits made to either are
overwritten on the next build.

```sh
python3 scripts/build.py       # the research page
python3 scripts/build_cv.py    # the CV
```

Quarto runs `build.py` automatically before every render, so `quarto preview`
picks up your changes as you save. `build_cv.py` you run yourself when the CV
changes — it needs Typst (`brew install typst`) and its output is a committed
PDF, so it is deliberately not part of the site render.

**A paper is described in exactly one place.** Both outputs read the same
`works.yml` and `people.yml`, so adding a publication updates the research
page and the CV together.

---

## Common tasks

### A paper got accepted

Find it in `works.yml` and change three things:

```yaml
- id: retail-price-holidays
  status: forthcoming          # was: working
  outlet: American Economic Review   # add this
  section: Journal Articles    # was: Working Papers
```

It moves out of Working Papers and into Journal Articles automatically, and
gains a "Forthcoming, *American Economic Review*" line.

### A forthcoming paper came out

```yaml
  status: published
  volume: 115
  issue: 4
  pages: 1109–1128
  year: 2026
```

Add `links:` for the publisher page while you're there:

```yaml
  links:
    - label: Published version
      url: https://doi.org/10.1257/aer.20240001
```

### Add a new working paper

Put the PDF in `assets/pdf/`, then add a record. Use the PDF's basename as the
`id` — that keeps ids short and memorable.

```yaml
- id: my-new-paper
  title: The Full Title, Capitalised As You Want It Displayed
  section: Working Papers
  status: working              # or under-review
  authors: [miller, benjamin-hansen]
  links:
    - label: Paper
      url: assets/pdf/my-new-paper.pdf
      note: (September 2026)
  abstract_heading: Abstract
  abstract: One paragraph, on one line. Long lines are fine.
```

Order within a section is the order in the file. Working papers are listed
newest draft first — on the CV, sorted by the draft date.

**The CV shows the date of the last draft**, which it takes from the `note:`
on the `Paper` link. A paper with no link needs the date stated outright, or
the CV build fails:

```yaml
- id: premerger-notification-matter-evidence
  draft: July 2016             # only needed when there is no Paper link
```

### Add a book chapter

Chapters take `editors`, which the CV cites and the research page ignores:

```yaml
- id: my-chapter
  section: Book Chapters
  outlet: Handbook of Something
  editors: Zimmermann, K. and Marcotte, D.
  pages: 338–344
  year: 2024
```

### Add a report in a numbered series

`number` gives both outputs the series number:

```yaml
- id: my-policy-brief
  section: Policy Reports & Media
  outlet: Cato Institute Research Brief in Economic Policy
  number: '125'
  year: 2018
```

### Change something on the CV only

Positions, education, grants, presentations, referee service, department and
university service, teaching, advising — none of these appear on the website,
so they live in `cv.yml`. Edit it and rebuild:

```sh
python3 scripts/build_cv.py
```

`cv.yml` also still holds `fields` and `honors`, which the current CV does not
render. They are kept so restoring either section is a change to
`scripts/cv/cv.typ`, not a retyping job.

### Add a coauthor

New people go in `people.yml`:

```yaml
jane-doe:
  name: Jane Doe                    # shown on the site
  url: https://janedoe.example      # optional; omit if they have no homepage
  cite: Doe, J.                     # used by the CV
```

Then reference the key in a paper's `authors:` list.

### Add press coverage

`media.yml`:

```yaml
- outlet: The Register-Guard
  month: October
  year: 2026
  title: Headline exactly as published
  url: https://...
  work: retail-price-holidays   # optional: which paper it covers
  note: on cannabis taxes       # optional: trailing clause
```

---

## Rules worth knowing

**Author lists include you, in the paper's real order.**

```yaml
authors: [benjamin-hansen, kendall-houghton, miller, caroline-weber]
```

The site prints all four names. The CV will print `Miller, K.` in bold in the
same position. Never leave yourself out — the build warns if you do.

A solo-authored paper (`authors: [miller]`) gets no author line at all.

**`status` decides which section a paper *reads* as**, but `section` decides
where it *appears*. Change both together when a paper is accepted.

Valid statuses: `working`, `under-review`, `forthcoming`, `published`.
Valid sections: `Journal Articles`, `Book Chapters`, `Working Papers`,
`Policy Reports & Media`.

**Citation fields are structured, not free text.** Give `volume`, `issue`,
`pages`, `year` separately and the page assembles `45(3): e70041, 2026`.
Omit what doesn't apply — a paper with only an article number just gets
`pages: nhaf034`.

**Ids are permanent.** They tie a paper to its PDF and to press coverage.
Renaming one means updating anything that points at it.

---

## Publishing

```sh
python3 scripts/build.py      # regenerate
quarto preview                # look at it (Ctrl-C to stop)
git add -A
git commit -m "Add new working paper on X"
git push                      # this deploys
```

Pushing to `main` deploys automatically. It takes about a minute; check
progress with `gh run list --limit 1`, and confirm with:

```sh
curl -sI https://keatonmiller.org/research.html | head -1
```

---

## When it breaks

**The build refuses to run.** It prints exactly what's wrong and does not write
anything. Typical:

```
works.yml[3] 'retail-price-holidays': unknown author 'hanson' — add it to data/people.yml
works.yml[7] 'my-paper': link 'Paper' points at assets/pdf/my-paper.pdf, which does not exist
```

Fix the file and run it again. Nothing is half-written.

**`error: PyYAML is not installed`** — run:

```sh
python3 -m pip install --user pyyaml
```

It has to be the same `python3` Quarto uses. Check with `which python3`.

**A YAML syntax error** (`could not find expected ':'`) is almost always
indentation, or a value containing a colon that needs quoting:

```yaml
title: "Sharing the Sacrifice: Optimal Wage Reductions"   # quoted — has a colon
```

**The deploy failed.** `gh run view --log-failed` shows why. The build runs the
same script in CI, so a data error fails there too — but it fails *before*
publishing, so the live site keeps serving the last good version.

**You edited `research.qmd` by mistake.** Nothing is lost from the site — just
run `python3 scripts/build.py` to regenerate it, and make the edit in `data/`
instead. `git checkout research.qmd` also works.

**Check without changing anything:**

```sh
python3 scripts/build.py --check       # is research.qmd current?
python3 scripts/build_cv.py --check    # is the CV PDF current?
```

Both exit non-zero if their output is out of date with `data/`.

---

## The files

| File | What it holds |
|---|---|
| `works.yml` | Every paper, chapter and report |
| `people.yml` | Coauthors: display name, homepage, citation form |
| `media.yml` | Press coverage |
| `_frontmatter.yml` | The research page's title and TOC settings |
| `cv.yml` | The CV's own sections: positions, education, grants, presentations, service, teaching, advising |
| `scripts/build.py` | Validates and generates `research.qmd` |
| `scripts/build_cv.py` | Validates and generates the CV PDF |
| `scripts/cv/cv.typ` | The CV's typesetting |
| `scripts/extract_research.py` | One-time bootstrap. Refuses to run now. Ignore it. |
