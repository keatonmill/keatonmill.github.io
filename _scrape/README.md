# Squarespace archive

Snapshot of the old keatonmiller.org Squarespace site, taken 2026-09-08 with
curl. The directory name starts with an underscore so Quarto ignores it when
rendering; it is kept in the repo for reference.

| Path | What |
|---|---|
| `raw/index.html`, `raw/research.html`, `raw/teaching.html` | Verbatim HTML of `/`, `/research`, `/teaching` |
| `index.md`, `research.md`, `teaching.md` | Main-content region of each page, converted to markdown with pandoc |
| `index.txt`, `research.txt`, `teaching.txt` | Same, as plain text |
| `asset-urls.txt` | Every `/s/<file>` link found across the three pages (18 files) |
| `assets/` | Those 18 files, downloaded with their original filenames, plus `headshot.jpg` |
| `raw/scholar.html`, `scholar.txt` | Google Scholar profile as fetched 2026-09-08, and a parsed listing |
| `migration-notes.md` | What changed when the research page was rebuilt, and what Keaton resolved |

All 18 assets were checked with `file` and are genuine PDFs (17) or a zip
archive (1); none is a saved error page. The headshot came from the
Squarespace CDN at
`images.squarespace-cdn.com/content/v1/56a1484625981dd79f45da68/1522705123570-UVF699YVKU2EX0J7ZUB2/headshot`;
the CDN serves WebP by default, so it was fetched with an `Accept: image/jpeg`
header to get the original 2500×1667 JPEG.

Three of the 18 assets are teaching-page syllabi that were not in the original
inventory: `ec201-`, `ec460-`, and `ec607-sample-syllabus-miller.pdf`.

The legacy files are served from `../s/` on the new site so old `/s/<file>`
URLs keep working (see the top-level README), except the three syllabi,
which were moved to `../assets/pdf/` in September 2026.
