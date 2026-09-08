# keatonmiller.org — Quarto website

Academic website for Keaton Miller, built with [Quarto](https://quarto.org) and
published to GitHub Pages at https://keatonmill.github.io (custom domain
keatonmiller.org pending). The layout and theme are adapted from David Evans's
site (`dgevans/dgevans.github.io`).

## Editing

Everything is plain markdown:

| File | Page |
|---|---|
| `index.qmd` | Home / about page |
| `research.qmd` | Publications, working papers, work in progress, policy & media |
| `teaching.qmd` | Courses, with collapsible descriptions |
| `404.qmd` | Not-found page (points stale paper links to Research) |
| `_quarto.yml` | Site title, navigation bar, footer |
| `theme.scss` | Colors and fonts (University of Oregon palette) |

To add a paper, copy one of the `:::: {.paper}` blocks in `research.qmd` and
edit the title, authors, links, and abstract.

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

### Updating a draft

Overwrite the file in `assets/pdf/` under the same name, change the date in
the link text in `research.qmd`, commit, push. The URL never changes, so
citations keep resolving to the current version. Superseded drafts remain in
git history:

```sh
git log --oneline -- assets/pdf/managed-competition.pdf
git show <commit>:assets/pdf/managed-competition.pdf > old-draft.pdf
```

### Adding a new paper

Drop the PDF in `assets/pdf/` with a short slug name and add a block to
`research.qmd`. Never put new files in `s/`.

### Retired links

A request for any missing path gets `404.html`, which tells readers looking
for a draft to go to the Research page. GitHub Pages cannot redirect a `.pdf`
URL, so this is the whole mechanism.

To update the CV, replace `assets/pdf/Keaton-Miller-CV.pdf` (same filename —
the navbar links to it directly).

## Previewing locally

```sh
quarto preview
```

## Publishing

The site deploys automatically via GitHub Actions
(`.github/workflows/publish.yml`) on every push to `main`. The Pages source
is set to **GitHub Actions**. (For a `<handle>.github.io` repo GitHub turns
Pages on in legacy Jekyll mode at the first push and that build can race the
Actions deploy; if the live site ever shows this README, re-run the
**Publish website** workflow.)

### Custom domain (keatonmiller.org)

1. After the site is live, set **Settings → Pages → Custom domain** to
   `keatonmiller.org`. (No CNAME file is needed with Actions-based deploys.)
2. Recommended: verify the domain account-wide (GitHub account
   **Settings → Pages → Add a verified domain**; add the provided
   `_github-pages-challenge-...` TXT record at the registrar).
3. At the registrar, replace the old Squarespace records with:
   - **A** record on the apex (blank record name) →
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
     `185.199.111.153` (one per line)
   - **CNAME** record `www` → `keatonmill.github.io`
4. Once the DNS check passes in **Settings → Pages**, enable
   **Enforce HTTPS**. GitHub then redirects www → apex automatically.
5. After a day of verified operation, cancel the Squarespace **website**
   plan — never the domain registration.

`_scrape/` holds the raw scrape of the old Squarespace site and the Google
Scholar profile for reference; it starts with an underscore, so Quarto
ignores it when rendering.
