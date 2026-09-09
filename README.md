# keatonmiller.org — Quarto website

Academic website for Keaton Miller, built with [Quarto](https://quarto.org) and
published to GitHub Pages at https://keatonmiller.org (the repo is
`keatonmill/keatonmill.github.io`). The layout and theme are adapted from
David Evans's site (`dgevans/dgevans.github.io`).

## Editing

Everything is plain markdown:

| File | Page |
|---|---|
| `index.qmd` | Home / about page |
| `data/*.yml` | Publications, working papers, policy & media — **the research page is generated from these** |
| `teaching.qmd` | Courses, with collapsible descriptions |
| `404.qmd` | Not-found page (points stale paper links to Research) |
| `_quarto.yml` | Site title, navigation bar, footer |
| `theme.scss` | Colors and fonts (University of Oregon palette) |

The research page is the one exception to "plain markdown": `research.qmd` is
**generated** from `data/*.yml` by `scripts/build.py`, which Quarto runs before
every render. Editing `research.qmd` directly does nothing lasting — the next
render overwrites it.

See **[`data/README.md`](data/README.md)** for how to add a paper, mark one
accepted, add a coauthor, or record press coverage.

## Where PDFs live

Two directories, on purpose:

- **`assets/pdf/`** — current files, one stable undated name per paper
  (`assets/pdf/faculty-unions.pdf`, `assets/pdf/Keaton-Miller-CV.pdf`, …).
  Link to them as `assets/pdf/<slug>.pdf`.
- **`s/`** — frozen archive of the old Squarespace site's `/s/<file>` URLs,
  which are cited in Google Scholar, CVs, and other people's papers. Every
  file there is published regardless of whether a page links to it
  (`project.resources` in `_quarto.yml`). **Do not add to, rename, or delete
  anything in `s/`.**
  (Exception already made: the three sample syllabi were moved to
  `assets/pdf/` in September 2026, since syllabus links are not cited.)

### Updating a draft

Overwrite the file in `assets/pdf/` under the same name, update that link's
`note:` in `data/works.yml`, commit, push. The URL never changes, so
citations keep resolving to the current version. Superseded drafts remain in
git history:

```sh
git log --oneline -- assets/pdf/managed-competition.pdf
git show <commit>:assets/pdf/managed-competition.pdf > old-draft.pdf
```

### Adding a new paper

Drop the PDF in `assets/pdf/` with a short slug name and add a record to
`data/works.yml` — use the PDF's basename as the paper's `id`. See
[`data/README.md`](data/README.md). Never put new files in `s/`.

### Retired links

A request for any missing path gets `404.html`, which tells readers looking
for a draft to go to the Research page. GitHub Pages cannot redirect a `.pdf`
URL, so this is the whole mechanism.

### The CV

The CV is **generated**, like the research page. `assets/pdf/Keaton-Miller-CV.pdf`
is a build product — do not replace it by hand.

```sh
python3 scripts/build_cv.py
```

Publications come from `data/works.yml` and `data/people.yml`, the same files
that drive the research page, so a paper is described in exactly one place.
The CV's own sections — positions, education, grants, presentations, service,
teaching, advising — live in `data/cv.yml`. The typesetting is
`scripts/cv/cv.typ`.

This needs Typst (`brew install typst`), so unlike `scripts/build.py` it is
**not** a Quarto pre-render step: the PDF is committed, and it rebuilds when
the CV changes rather than on every site render. `--check` exits non-zero if
the committed PDF is out of date with `data/`.

The filename never changes — the navbar links to it directly.

## Previewing locally

One-time setup — the render step needs PyYAML, in whichever `python3` Quarto
finds on your PATH:

```sh
python3 -m pip install --user -r requirements.txt
```

Then:

```sh
quarto preview
```

`quarto preview` regenerates `research.qmd` from `data/` on every save, so
edits to the YAML show up live.

## Publishing

The site deploys automatically via GitHub Actions
(`.github/workflows/publish.yml`) on every push to `main`. The Pages source
is set to **GitHub Actions**. (For a `<handle>.github.io` repo GitHub turns
Pages on in legacy Jekyll mode at the first push and that build can race the
Actions deploy; if the live site ever shows this README, re-run the
**Publish website** workflow.)

### Custom domain (keatonmiller.org)

Done on 8 September 2026. The current setup, for reference:

- **Registrar:** Tucows, managed through the Squarespace dashboard. Renews
  2027-01-22 — leave auto-renew on. Cancelling the Squarespace *website*
  plan must never touch the *domain registration*.
- **Nameservers:** unchanged, still Squarespace's
  (`ns01–04.squarespacedns.com` plus `dns1–4.p06.nsone.net`), so DNS
  records are edited in the Squarespace DNS panel.
- **Records:** apex A → `185.199.108.153`, `185.199.109.153`,
  `185.199.110.153`, `185.199.111.153`; `www` CNAME →
  `keatonmill.github.io`; plus the `_github-pages-challenge-keatonmill` TXT
  record that verifies the domain against the GitHub account (keep it — it
  stops anyone else claiming the domain on their own Pages site). There are
  no MX records; the domain carries no email.
- **Repo side:** **Settings → Pages → Custom domain** is
  `keatonmiller.org` with **Enforce HTTPS** on. No `CNAME` file is needed
  with Actions-based deploys — the setting lives in the Pages config. If a
  deploy ever clears it, add a `CNAME` file containing the domain to
  `project.resources` in `_quarto.yml`.

To roll back to Squarespace: restore the apex A records
`198.185.159.144/145` and `198.49.23.144/145`, point `www` at
`ext-sq.squarespace.com`, and reconnect the domain to the Squarespace site.

`_scrape/` holds the raw scrape of the old Squarespace site and the Google
Scholar profile for reference; it starts with an underscore, so Quarto
ignores it when rendering.
