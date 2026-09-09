// The CV's typesetting. Data comes from scripts/cv/content.json, which
// scripts/build_cv.py generates from data/works.yml, data/people.yml and
// data/cv.yml -- do not edit that JSON, and do not put content here.
//
//     python3 scripts/build_cv.py
//
// The layout rules that matter, in case they need defending later:
//
//   * ONE date column. Every date sits in the same gutter, and every wrapped
//     line aligns to the content column, so a continuation can never be read
//     as a new entry. GUT is set by the widest label -- "2023-present"
//     measures 0.857in -- not by the dates.
//   * Section rules span the full measure even above two-column blocks.
//   * Dates are set at body size so they sit ON an entry's first line rather
//     than floating above it.
//   * Ragged right. Justifying opened rivers in the dense lists.
//   * More space above a heading than below it, so each heading groups with
//     the content it introduces.
//   * In two-column blocks the columns are too narrow for a gutter, so the
//     year leads its own line. That is the one deliberate exception, and it
//     is what lets those sections set two-up.
//   * `fields` and `honors` are in data/cv.yml but not rendered. Restoring
//     either is a section added here.
//
// Accent colour: --input accent=slate (default) or accent=oxblood.

#let C = json("content.json")

#let ACCENTS = (
  slate:   rgb("#33556e"),
  oxblood: rgb("#7a3140"),
)
#let accent = ACCENTS.at(sys.inputs.at("accent", default: "slate"))

#let INK = rgb("#222222")
#let DIM = rgb("#6a6a6a")
#let SERIF = ("Charter", "Georgia")
#let SANS = ("Helvetica Neue", "Helvetica")

#let GUT = 0.88in   // the date column
#let GAP = 0.20in   // and the space after it

#set document(
  title: C.meta.name + " – Curriculum Vitae",
  author: "Keaton Miller",
  description: "Curriculum Vitae of " + C.meta.name + ", " + C.meta.role,
  keywords: ("economics", "industrial organization", "health economics",
             "University of Oregon"),
)
#set page(
  paper: "us-letter",
  margin: (left: 0.8in, right: 0.8in, top: 0.75in, bottom: 0.7in),
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 8pt, font: SANS, fill: DIM)
      grid(columns: (1fr, auto),
        text(fill: accent, weight: 600)[#C.meta.name],
        [Curriculum Vitae #h(0.5em) #counter(page).display()])
      v(-0.45em)
      line(length: 100%, stroke: 0.4pt + rgb("#d8d8d8"))
    }
  },
)
#set text(font: SERIF, size: 9.8pt, fill: INK, hyphenate: false)
#set par(leading: 0.5em, justify: false)   // ragged right
#show link: it => it                        // black on paper, live on screen

// ---------- pieces ----------

#let authors(a) = {
  let parts = a.map(p => if p.at(1) { strong(p.at(0)) } else { p.at(0) })
  if parts.len() == 1 { parts.at(0) } else {
    for (i, p) in parts.enumerate() {
      if i == 0 { p } else if i == parts.len() - 1 { [, and ]; p } else { [, ]; p }
    }
  }
}

#let titled(e) = {
  let t = "“" + e.title + "”"
  if e.url != none { link(e.url, t) } else { t }
}

#let pub(e) = {
  authors(e.authors)
  [ ]
  titled(e)
  [ ]
  if "prefix" in e { e.prefix }
  if e.outlet != none { emph(e.outlet) }
  if e.at("forthcoming", default: false) { [, ]; emph[forthcoming]; [.] }
  // boxed so a page range like 479-487 cannot break across two lines
  else if e.detail != "" { [ ]; box(e.detail); [.] }
  else { [.] }
}

// a section heading: full measure, always, whatever is underneath it
#let sec(name) = {
  v(1.6em, weak: true)
  block(breakable: false, sticky: true, width: 100%, spacing: 0em, stack(dir: ttb,
    text(font: SERIF, size: 8.8pt, weight: 700, fill: accent, tracking: 0.12em,
      upper(name)),
    v(3pt),
    line(length: 100%, stroke: 0.7pt + accent),
  ))
  v(0.3em, weak: true)
}

// the date, at body size so it sits on the entry's first line
#let date(s) = text(fill: accent, weight: 600)[#s]

// one entry: date in the gutter, everything else in the content column,
// so wrapped lines align under the first line and never under the date
#let dated(label, body) = block(width: 100%, breakable: false, spacing: 0.6em,
  grid(columns: (GUT, GAP, 1fr), align: (right + top, left, left + top),
    date(label), [], body))

// One item in a list. The hanging indent marks a wrapped line as a
// continuation rather than the next item, and must be set on the paragraph
// itself -- an enclosing `set par` does not reach in here.
#let li(body, gap: 0.35em) = block(width: 100%, spacing: gap,
  par(hanging-indent: 0.9em, body))

// inside a two-column block the gutter will not fit, so the year leads
#let led(label, items) = block(width: 100%, breakable: false, spacing: 0.55em, {
  date(label); linebreak()
  items.map(i => li(i)).join()
})

// anything with no date of its own still starts at the content column
#let indented(body) = pad(left: GUT + GAP, body)

// split a list of (cost, content) pairs into two columns of roughly equal
// height, reading down the left column and then down the right
#let balanced(items, gutter: 1.6em) = {
  let total = items.fold(0, (a, it) => a + it.at(0))
  let run = 0
  let cut = items.len()
  for (i, it) in items.enumerate() {
    if run >= total / 2 and cut == items.len() { cut = i }
    run += it.at(0)
  }
  grid(columns: (1fr, 1fr), column-gutter: gutter, align: (left + top, left + top),
    items.slice(0, cut).map(it => it.at(1)).join(),
    items.slice(cut).map(it => it.at(1)).join())
}

// ---------- masthead ----------

#block(width: 100%, {
  grid(columns: (1fr, auto), align: (left + bottom, right + bottom),
    text(font: SANS, size: 20pt, weight: 600, fill: INK, tracking: -0.01em)[#C.meta.name],
    {
      set text(size: 8.4pt, font: SANS, fill: DIM)
      align(right, {
        C.meta.address.join(" · ")
        linebreak()
        link("mailto:" + C.meta.email)[#C.meta.email]
        [ · ]
        link(C.meta.website_url)[#C.meta.website]
      })
    })
  v(0.35em)
  line(length: 100%, stroke: 1.6pt + accent)
  v(0.3em)
  set text(size: 8.6pt, font: SANS, fill: DIM)
  [#C.meta.role]
})

// ---------- full-measure sections ----------

#sec("Academic Positions")
#for p in C.positions { dated(p.years, p.what) }

#sec("Education")
#for e in C.education {
  dated(e.year, {
    e.lines.at(0)
    for l in e.lines.slice(1) { linebreak(); text(size: 9.2pt, fill: DIM)[#l] }
  })
}

#sec("Publications in Refereed Journals")
#for e in C.journals {
  dated(if e.year == none { text(size: 8.6pt)[forthcoming] } else { str(e.year) }, pub(e))
}

#sec("Contributions to Edited Volumes")
#for e in C.chapters { dated(str(e.year), pub(e)) }

#sec("Working Papers")
#for e in C.working {
  dated(
    if e.draft == none { text(fill: DIM)[#sym.dash.em] } else { text(size: 8.8pt)[#e.draft] },
    { authors(e.authors); [ ]; titled(e) },
  )
}

#sec("Other Publications")
#for e in C.other { dated(str(e.year), pub(e)) }

#sec("Grants")
#for g in C.grants {
  dated(g.years, {
    strong(g.role); [, ]; g.source; linebreak()
    emph(g.title); [. ]; text(fill: DIM)[#g.amount#[.]]
  })
}

#sec("Teaching")
#for t in C.teaching {
  block(width: 100%, breakable: false, spacing: 0.6em, indented({
    t.course; linebreak(); text(size: 9.2pt, fill: DIM)[#emph(t.note)]
  }))
}

// ---------- two-column sections ----------
// The rule above each of these still spans the full measure; only the content
// splits, which is what C got wrong.

#sec("Presentations")
#balanced(C.presentations.map(p => (p.items.len() + 1, led(p.year, p.items))))

#sec("Professional Referee Service")
#block(breakable: false, indented({
  set text(size: 9.3pt)
  balanced(C.referee.map(j => (1, li(emph(j)))))
}))
#v(0.5em)
#dated("Grant review", C.grant_review.join("; ") + ".")

#sec("Department Service")
#balanced(C.dept_service.map(s => (s.items.len() + 1, led(s.years, s.items))))

#sec("University and External Service")
#balanced(C.univ_service.map(s => (s.items.len() + 1, led(s.years, s.items))))

#sec("Graduate Advising")
#dated("Current", C.advising.current.map(s => [#s]).join(linebreak()))
#v(0.35em)
#dated("Past", text(size: 9.2pt, fill: DIM)[#emph[by role, then alphabetically, with initial placement]])
#v(-0.25em)
#block(breakable: false, indented({
  set text(size: 9.4pt)
  // ~40 characters to the line at this width, so long placements cost two
  balanced(C.advising.past.map(s => (calc.ceil(s.len() / 40), li(s))))
}))

#sec("Undergraduate Advising")
#for s in C.advising.undergraduate { block(spacing: 0.55em, indented(s)) }
