# keatonmiller.org — Quarto site

Personal academic site for Keaton Miller (Associate Professor of Economics
and Director of Graduate Studies, University of Oregon). Quarto website on
GitHub Pages, adapted from David Evans's site (`dgevans/dgevans.github.io`,
local clone at `../dgevans.github.io`).

Read `README.md` for the editing and file-layout conventions; they are the
source of truth. This file covers what the README doesn't.

## Status (as of 2026-09-08)

- Migration from Squarespace is complete and live at
  https://keatonmiller.org (repo `keatonmill/keatonmill.github.io`,
  Pages source: GitHub Actions).
- DNS cutover is done. The domain is registered at Tucows via Squarespace
  and still uses Squarespace's nameservers; only the records changed. The
  README's "Custom domain" section records the setup and the rollback.
- Still open: cancel the Squarespace **website** plan after a few days of
  clean operation — never the domain registration.
- `_scrape/migration-notes.md` records what changed vs. the old site and
  what Keaton has resolved.

## Ground rules

- Do not touch DNS or Squarespace settings without Keaton doing the
  clicking; never delete anything from Squarespace.
- Never add to, rename, or delete files in `s/` (frozen legacy URLs).
- Do not invent paper metadata (dates, outlets, coauthors, DOIs). Sources are
  the scrape, Google Scholar (Keaton has approved it as a source), publisher
  pages, or Keaton.
- Use published abstracts for published papers. ScienceDirect blocks
  automated access; Crossref, Semantic Scholar and OpenAlex do not carry
  Elsevier abstracts, so those come from Keaton.
- Commit in small, described steps. Pushing to `main` deploys.

## Environment notes

- The Bash tool's shell sometimes has a stripped PATH; start commands with
  `export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/anaconda3/bin:$PATH`.
- `gh` is installed and logged in as keatonmill and is git's credential
  helper for github.com. Push over HTTPS; the local SSH key is not
  registered with GitHub.
- `.claude/launch.json` (gitignored) starts `quarto preview` on port 4321
  for the in-app browser.

## Open items

- Two *Journal of Public Economics* abstracts and the *Research in
  Transportation Economics* abstract may still be working-paper text.
- "In Search of Peace and Quiet" may be defunct; Keaton is undecided.
- Keaton plans to update the CV again (January 2026 version is live).
- Theme: still David's UO green/yellow; Keaton hasn't asked for changes.
