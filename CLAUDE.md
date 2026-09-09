# keatonmiller.org — Quarto site

Personal academic site for Keaton Miller (Associate Professor of Economics
and Director of Graduate Studies, University of Oregon). Quarto website on
GitHub Pages, adapted from David Evans's site (`dgevans/dgevans.github.io`,
local clone at `../dgevans.github.io`).

Read `README.md` for the editing and file-layout conventions, and
`data/README.md` for how to change anything on the research page; they are
the source of truth. This file covers what they don't.

## The research page is generated — do not hand-edit it

`research.qmd` is a **build product**. It is generated from `data/*.yml` by
`scripts/build.py`, which Quarto runs as a `pre-render` step, so any edit
made directly to `research.qmd` is overwritten on the next render. The file
carries a `GENERATED FILE` banner in its front matter saying so.

- `data/works.yml` — every paper, chapter and report
- `data/people.yml` — coauthors: display name, homepage, `cite:` form
- `data/media.yml` — press coverage
- `data/cv.yml` — the CV-only sections (positions, education, grants,
  presentations, service, teaching, advising)
- `scripts/build.py` — validates `data/` and generates `research.qmd`.
  Quarto's pre-render step. `--check` exits non-zero if it is stale.
- `scripts/build_cv.py` — validates and generates the CV PDF. Run by hand;
  needs Typst. `--check` exits non-zero if the committed PDF is stale.
- `scripts/extract_research.py` — the one-time bootstrap that created
  `data/`. It refuses to run now; do not use it.

Each work carries the **full author list in the paper's own order,
including Keaton** (`authors: [benjamin-hansen, ..., miller, ...]`). The
site renders every name; the CV will render `Miller, K.` in bold in the
same position. `status` is one of `working`, `under-review`, `forthcoming`,
`published`; `section` decides where an entry appears, so change both when
a paper is accepted. Ids are permanent — they tie a paper to its PDF and to
press coverage.

Validation is strict and writes nothing when it fails: unknown author keys,
bad statuses or sections, duplicate ids, published work with no year or
outlet, media pointing at a missing work, and local links whose file is not
in the repo. CI runs the same script, so a data error fails the build
*before* publishing and the live site keeps serving the last good version.

## Status (as of 2026-09-09)

- Migration from Squarespace is complete and live at
  https://keatonmiller.org (repo `keatonmill/keatonmill.github.io`,
  Pages source: GitHub Actions).
- DNS cutover is done. The domain is registered at Tucows via Squarespace
  and still uses Squarespace's nameservers; only the records changed. The
  README's "Custom domain" section records the setup and the rollback.
- Still open: cancel the Squarespace **website** plan — never the domain
  registration.
- `_scrape/migration-notes.md` records what changed vs. the old site and
  what Keaton has resolved.

## Ground rules

- Do not touch DNS or Squarespace settings without Keaton doing the
  clicking; never delete anything from Squarespace.
- Do not add to, rename, or delete files in `s/` (frozen legacy URLs)
  without Keaton explicitly asking. He authorised one deletion in September
  2026 — `s/miller-cv-web-2023-10-18.pdf`, an old CV carrying his personal
  cell number, which was being served publicly. Do not restore it. The URL
  now 404s, which routes to `404.html`.
- Do not invent paper metadata (dates, outlets, coauthors, DOIs). Sources are
  the scrape, Google Scholar (Keaton has approved it as a source), publisher
  pages, or Keaton. When only initials are known for a coauthor, ask — do
  not expand them to a guessed first name.
- Use published abstracts for published papers. ScienceDirect blocks
  automated access; Crossref, Semantic Scholar and OpenAlex do not carry
  Elsevier abstracts, so those come from Keaton.
- Commit in small, described steps. Pushing to `main` deploys.

## The CV

`assets/pdf/Keaton-Miller-CV.pdf` is a **build product** — do not replace it by
hand, and do not hand-edit it.

```sh
python3 scripts/build_cv.py
```

- Publications come from `data/works.yml` + `data/people.yml`; the CV-only
  sections from `data/cv.yml`. A paper is described in exactly one place.
- `scripts/cv/cv.typ` is the typesetting, in Typst. It documents the layout
  rules and why they are what they are — read it before changing spacing.
- `scripts/cv/content.json` is a generated intermediate. Gitignored.
- Needs Typst (`brew install typst`). Deliberately **not** a Quarto pre-render
  step: the PDF is committed, and CI has no Typst.
- Layout as of September 2026: 5 pages, one date gutter, full-width section
  rules, two balanced columns for the list-heavy sections, slate `#33556e`
  accent. `fields` and `honors` are in `cv.yml` but not rendered.
- Dated source copies of the old Word CV are in `~/Dropbox/portfolio/` as
  `miller-cv-web-<date>.{docx,pdf}`. The Word pipeline is retired;
  `scripts/cv-prototype/` still holds it if a `.docx` is ever needed.

## Date tracking, for review-period reports

Merit and 3PTR reviews need "what did you do between date A and date B",
usually as the CV with the period's items highlighted. The data carries dates
the CV never prints so that report can be generated.

- **`accepted:` in `works.yml` is the operative date for a publication**, not
  `year`. The department's merit form is explicit: the date on the editor's
  acceptance letter marks the timing. Three works were accepted in a different
  year than they were published.
- Windows are arbitrary dates, not years — the 2026 merit window was
  Sept 16 2023 – Mar 20 2026, and the 3PTR used a different one. Never bake a
  window in.
- `referee.assignments` in `cv.yml` is one line per report submitted. 63 are
  recorded, 2016–2026, recovered from `~/Dropbox/editorial` (one folder per
  year; each report's own first line names its journal and manuscript id —
  the filename prefixes are editorial-system codes and are not always the
  journal you would guess). The date is the report file's mtime, the day the
  report was finished. A manuscript id ending in R1/R2/R3 is a revision, and
  Keaton writes a report on one only when he is not yet satisfied — a
  revision on disk with no report beside it is a sign-off, not a gap. The 7
  sign-offs are logged too, noted `sign-off, no report` and dated by the day
  the revision arrived, since there is no report to date them by.
  `referee.journals` remains the list the CV prints, and
  a journal that appears only in `assignments` is added to it automatically.
  `assignments` is journal peer review only. `~/Dropbox/editorial` also holds
  grant reviews (NSF, Russell Sage, Swiss NSF — see `grant_review`, which
  carries no dates) and, in `2023/`, a review of an internal Paragon Health
  Institute report. Keaton has decided the Paragon one does not belong on the
  CV: the piece is opinionated advocacy and he was checking its factual basis,
  not refereeing it. Do not add it.
- `teaching[].offerings` are the terms actually taught; `count` is the
  lifetime total the CV prints. An offering is a **section**, not a term:
  Spring 2017 was two sections of EC 201, so it is listed twice. Terms come
  from the per-term course folders in `~/Dropbox/teaching` (one folder per
  course per term), cross-checked against each syllabus's CRN line. Every
  offering is now dated; `count` should equal `len(offerings)`.
- `advising.past[].completed` is the defence **term** (`Spring 2026`), not
  a year -- windows split academic years. Unknown for all 14. Undergraduate
  advising takes the same field; it is not yet in the coverage report.
- `python3 scripts/build_cv.py --coverage [--since --until]` reports what is
  dated and what falls in a window.
- Sources: `~/Dropbox/portfolio/acceptance letters/` (dated filenames),
  `~/Dropbox/editorial/<year>/` (referee reports),
  `~/Dropbox/department/faculty-activity-reports/`, and
  `~/Dropbox/portfolio/miller-cv-annotated-2026-02-13.docx` (the highlighted
  3PTR CV — highlight runs are recoverable from the docx XML).

## Environment notes

- The Bash tool's shell sometimes has a stripped PATH; start commands with
  `export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/anaconda3/bin:$PATH`.
- `gh` is installed and logged in as keatonmill and is git's credential
  helper for github.com. Push over HTTPS; the local SSH key is not
  registered with GitHub.
- `.claude/launch.json` (gitignored) starts `quarto preview` on port 4321
  for the in-app browser.
- **The build needs PyYAML** in whichever `python3` Quarto finds — that is
  `/usr/bin/python3` here, not Anaconda's. `python3 -m pip install --user -r
  requirements.txt`. The deploy workflow installs it separately.
- **There is no LibreOffice on this machine.** Microsoft Word renders the
  CV's PDF, driven by AppleScript (`open`, then `save as document 1 ...
  file format format PDF`). Word is also the more faithful renderer.
- `exiftool` sets PDF Title/Author metadata, which Word's export drops.

## Open items

- Two *Journal of Public Economics* abstracts and the *Research in
  Transportation Economics* abstract may still be working-paper text.
- "In Search of Peace and Quiet" may be defunct; Keaton is undecided.
- The abstract for the climate change / Oregon household budgets working
  paper was taken from the PDF; Keaton has not confirmed it is the version
  he wants public.
- Two publisher links could not be verified (ScienceDirect and University of
  Chicago Press both return 403 to automated requests): the *Journal of
  Public Economics* vertical-integration paper and the *National Tax
  Journal* cannabis-legalization paper.
- Theme: still David's UO green/yellow; Keaton hasn't asked for changes.
