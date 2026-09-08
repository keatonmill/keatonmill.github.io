# keatonmiller.org — Quarto site migration

Context for Claude Code. Read this fully before doing anything.

## What this is

Personal academic site for Keaton Miller — Associate Professor of Economics
and Director of Graduate Studies, University of Oregon. Migrating from
Squarespace to a Quarto website on GitHub Pages, modeled on David Evans's
site (https://econevans.com, repo `dgevans/dgevans.github.io`). A local clone
of David's repo should be at `../dgevans.github.io` — confirm the path with
Keaton if it isn't there.

Strategy was worked out in a claude.ai chat on 2026-09-08. This file is the
handoff. Work through the phases in order and check in with Keaton between
phases.

## Ground rules

- Squarespace stays live until the new site is verified on GitHub. Do not
  touch DNS or Squarespace settings — Phase 5 happens only when Keaton says go.
- Never delete anything from Squarespace.
- Commit in small, described steps. Ask before the first push.
- Do not invent paper metadata (dates, outlets, coauthors, DOIs). Everything
  comes from the Squarespace scrape or from Keaton.
- Keep David's theme and layout as-is initially; visual tweaks come last.

## Phase 0 — Scaffold from David's template

Copy from `../dgevans.github.io`, excluding `.git/`, `_site/`, `.quarto/`,
`_scrape/`, `assets/pdf/*`, and `assets/img/headshot.jpg`:

- `_quarto.yml`, `theme.scss`, `index.qmd`, `research.qmd`, `teaching.qmd`
- `.github/workflows/publish.yml` — the Actions deploy; required
- `fix-links.py` — post-render hook referenced in `_quarto.yml`. Read it,
  note what it does, and keep it unless it's David-specific.
- `assets/img/favicon.ico`, `README.md`

Then `git init`. Replace David's name, email, office, bio, and CV filename in
`_quarto.yml` and `index.qmd`:

- Title: Keaton Miller
- Role line: Associate Professor of Economics / Director of Graduate Studies
- Email: keatonm [at] uoregon.edu
- Office: Department of Economics, 435 PLC, 1285 University of Oregon,
  Eugene, OR 97403-1285
- Footer: © 2026 Keaton Miller · Department of Economics, University of Oregon
- CV link: `assets/pdf/Keaton-Miller-CV.pdf` (Keaton will supply a fresh one;
  use the 2023 PDF from the scrape as a placeholder)

Rewrite `README.md` for Keaton (same structure, his names/paths).

## Phase 1 — Archive Squarespace

Scrape the old site into `_scrape/` (underscore prefix = Quarto ignores it).
Pages: https://www.keatonmiller.org/ , /research , /teaching. Save raw HTML
plus a clean text/markdown rendering of each.

Download every asset. Known asset URLs (all under
https://www.keatonmiller.org unless noted). The teaching page was not
inspected in the chat — scrape it and check for more.

```
/s/miller-cv-web-2023-10-18.pdf
/s/2022-01-27-cannabis-wages-resubmission.pdf
/s/2019-01-05-tax-revenues-substances-RESTAT.pdf
/s/2020-08-17-revision-full-manuscript.pdf
/s/ntj-forum-preprint.pdf
/s/2024-06-23-servicer-reforms.pdf
/s/2024-06-24-in_app_billing.pdf
/s/2023-01-20-Optimal_Managed_Competition_Subsidies-paper.pdf
/s/mc_release.zip
/s/2022-04-01-rsue-resubmission-paper.pdf
/s/2022-02-08-ma-bid.pdf
/s/2022-01-tax-invariance-draft.pdf
/s/2019-06-30-ma-costs-RAND.pdf
/s/costs-benefits-civil-feb-28.pdf
/s/price-promotion-holidays-2.pdf
```

Headshot:
https://images.squarespace-cdn.com/content/v1/56a1484625981dd79f45da68/1522705123570-UVF699YVKU2EX0J7ZUB2/headshot
→ save as `assets/img/headshot.jpg` (check the actual format with `file`).

Verify every download with `file` — a Squarespace error page saved as `.pdf`
is the classic failure.

## Phase 2 — Preserve old URLs

Old PDF links are `/s/<filename>` and are cited in Google Scholar, CVs, and
other people's papers. Keep them working: put the legacy files in an `s/`
directory at the repo root, with their original filenames, and link to them
from `research.qmd` as `s/<filename>`. Use real files, not symlinks. New
papers added later go in `assets/pdf/` per David's convention — the README
should explain both locations.

Page URLs survive automatically: GitHub Pages serves `/research` as
`research.html`.

## Phase 3 — Content migration

Rebuild `research.qmd` from the scrape using David's block format:

```
:::: {.paper}
### Title

[with Coauthor A and Coauthor B]{.authors}\
[*Journal*, Volume(Issue): pages, Year]{.outlet}

[[Paper](s/file.pdf) · [Published version](https://doi.org/...)]{.paper-links}

::: {.callout-note appearance="simple" collapse="true" icon="false"}
## Abstract
...
:::
::::
```

Sections: Publications, Working Papers, Work in Progress (WIP entries are
titles + coauthors only, no block needed — see David's file).

Known fixes to make while migrating:

- The Squarespace "Work in Progress" list duplicates two papers that are
  already under Working Papers (Chang — mobile in-app billing; Martinez-Lazo —
  mortgage servicing). Drop the duplicates; keep the other two WIP items.
- Two Squarespace entries use `##` instead of `###` for titles (Vertical
  Integration / GRT paper; Tax Invariance paper). Normalize.
- Keep the "News coverage in the Wall Street Journal" link on the tax
  revenues paper. Consider a small "Policy & Media" section or page — his bio
  names policy engagement as one of three research themes.
- Where an entry links only to a publisher page, keep it as "Published
  version"; where a draft PDF exists, link it as "Paper" — same labeling as
  David.
- Draft dates ("June 2024") can go in the `.paper-links` line as plain text.
- Flag to Keaton anything that looks stale (working papers with 2018–2019
  drafts, status lines like "Under Review") rather than guessing.

Rebuild `teaching.qmd` from the scrape in David's format. Rebuild `index.qmd`
with Keaton's current bio paragraph from the scrape (Keaton may want to
revise it — offer).

## Phase 4 — Deploy to github.io

```
gh repo create <handle>.github.io --public --source=. --push
```

Then in the repo: Settings → Pages → Source: **GitHub Actions**. Confirm the
workflow runs green and the site renders at https://<handle>.github.io.
Have Keaton review every page before Phase 5.

## Phase 5 — DNS cutover (only when Keaton says go)

Registrar: **TBD — Keaton to confirm.** If the domain is at Squarespace
(likely, if it came over from Google Domains), it stays there; only the DNS
records change.

Per David's README:

1. Settings → Pages → Custom domain: `keatonmiller.org`. No CNAME file is
   needed with Actions-based deploys.
2. Verify the domain account-wide: GitHub account Settings → Pages → Add a
   verified domain; add the `_github-pages-challenge-...` TXT record at the
   registrar.
3. At the registrar, replace the Squarespace records with:
   - A (apex) → 185.199.108.153, 185.199.109.153, 185.199.110.153,
     185.199.111.153
   - CNAME `www` → `<handle>.github.io`
4. When the DNS check passes, enable **Enforce HTTPS**. GitHub redirects
   www → apex automatically.
5. After a day of verified operation, Keaton cancels the Squarespace
   **website** plan — never the domain registration.

## Open questions for Keaton

- GitHub handle (decides the repo name)?
- Where is keatonmiller.org registered?
- Fresh CV to replace the October 2023 PDF?
- Any bio or title changes beyond adding the DGS role?
- Keep the UO green/yellow theme, or something else?
