# CV builder — prototype

This generated the CV currently live at `assets/pdf/Keaton-Miller-CV.pdf`
(September 2026). It is **kept for reference, not wired into anything**: no
build step runs it, and `scripts/build.py` does not know it exists.

It is here because the design conversation for the CV is unfinished — layout
options still need comparing before committing to a generator — and this is the
working starting point.

## Running it

```sh
cd scripts/cv-prototype
npm install          # installs the `docx` package
node build.js out.docx
```

To get a PDF, open the `.docx` in Word and export. LibreOffice is not installed
on this machine; Word's own export is what produced the live PDF, and it is the
more faithful renderer anyway.

Output is not byte-reproducible — `docx` stamps a creation time and fresh
paragraph ids on every run — but the content is stable. Compare runs with
`pandoc -t plain`, not `md5`.

## The two files

**`data.js`** is the valuable one: the entire CV as structured data — positions,
education, publications, chapters, working papers, grants, presentations,
referee service, department and university service, teaching, advising, honours.
This is the raw material for a future `data/cv.yml`, already cleaned up:

- typos fixed (Garcia, European **Association**, Midwest **Economics**
  Association, University of Rochester, Dartmouth College)
- citations completed with page ranges
- the traffic-fatalities paper corrected from 2018 to 2020
- the *Health Affairs* SEO subtitle dropped

**`build.js`** holds the layout decisions worth carrying forward regardless of
what generates the CV in the end:

- Cambria 10.5pt (ships with Office on both platforms, so it never substitutes)
- five real named styles rather than direct formatting
- one content column at 1.083" everywhere
- `keepNext` on headings and subheads, `keepLines` on entries — no orphaned
  headings, no entry split across a page break
- paper titles unbolded, own name bolded in author lists instead
- titles hyperlinked to publisher pages, deliberately *not* styled as
  hyperlinks, so they stay black on paper but click through on screen
- referee service in two columns

That combination took the CV from 8 pages to 6.

## Known gap

Author lists in `data.js` are literal strings (`"Hansen, B., Houghton, K.,
Miller, K., and Weber, C."`). They should come from `data/works.yml` and
`data/people.yml` instead — those already carry the full author list in each
paper's real order, and `people.yml` has the `cite:` forms. Wiring that up
removes the last place where the CV and the site hold the same facts separately.

`data.js` also holds sections the site has no equivalent for — service,
teaching, presentations, advising, honours. Those need no reconciliation; they
just need somewhere to live.
