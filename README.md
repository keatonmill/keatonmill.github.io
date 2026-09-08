# keatonmiller.org — Quarto website

Academic website for Keaton Miller, built with [Quarto](https://quarto.org) and
published to GitHub Pages. The layout and theme are adapted from David Evans's
site (`dgevans/dgevans.github.io`).

## Editing

Everything is plain markdown:

| File | Page |
|---|---|
| `index.qmd` | Home / about page |
| `research.qmd` | Publications, working papers, work in progress |
| `teaching.qmd` | Courses |
| `_quarto.yml` | Site title, navigation bar, footer |
| `theme.scss` | Colors and fonts (University of Oregon palette) |

To add a paper, copy one of the `:::: {.paper}` blocks in `research.qmd` and
edit the title, authors, links, and abstract.

### Where PDFs live

There are two PDF directories, on purpose:

- `s/` — legacy files carried over from the Squarespace site, with their
  original filenames. The old site served them at `/s/<filename>`, and those
  URLs are cited in Google Scholar, CVs, and other people's papers, so they
  must keep working. Do not rename or move anything in `s/`. Link to them as
  `s/<filename>`.
  `_quarto.yml` lists `s/` under `project.resources`, so every file there is
  published even if no page links to it.
- `assets/pdf/` — everything new. Drop a new PDF here and link to it as
  `assets/pdf/yourfile.pdf`.

To update the CV, replace `assets/pdf/Keaton-Miller-CV.pdf` (same filename —
the navbar links to it directly).

## Previewing locally

```sh
quarto preview
```

## Publishing

The site deploys automatically via GitHub Actions
(`.github/workflows/publish.yml`) on every push to `main`.

One-time setup after creating the GitHub repository:

1. Push this folder to the repository.
2. In the repo settings, go to **Settings → Pages** and set **Source** to
   **GitHub Actions**. For a `<handle>.github.io` repo GitHub turns Pages on
   automatically in legacy (Jekyll, deploy-from-branch) mode the moment the
   first push lands, and that Jekyll build can race the Actions deploy and
   overwrite it. If the live site shows the README instead of the home page,
   switch the source to GitHub Actions and re-run the workflow (Actions →
   Publish website → Run workflow).

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
   - **CNAME** record `www` → `<handle>.github.io`
4. Once the DNS check passes in **Settings → Pages**, enable
   **Enforce HTTPS**. GitHub then redirects www → apex automatically.
5. After a day of verified operation, cancel the Squarespace **website**
   plan — never the domain registration.

`_scrape/` holds the raw scrape of the old Squarespace site for reference; it
starts with an underscore, so Quarto ignores it when rendering.
