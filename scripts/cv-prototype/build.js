const {Document, Packer, Paragraph, TextRun, Tab, TabStopType, AlignmentType,
  BorderStyle, Header, PageNumber, Table, TableRow, TableCell, WidthType,
  ExternalHyperlink, HeadingLevel} = require('docx');
const fs = require('fs');
const D = require('./data.js');

const FONT = "Cambria";
const SZ = 21;            // 10.5pt
const COL = 1560;         // the single content column
const RULE = {style: BorderStyle.SINGLE, size: 4, color: "A6A6A6", space: 3};

// ---------- run helpers ----------
const MK = "Miller, K.";
function authorRuns(a) {
  const out = [];
  a.split(MK).forEach((p, i, arr) => {
    if (p) out.push(new TextRun(p));
    if (i < arr.length - 1) out.push(new TextRun({text: MK, bold: true}));
  });
  return out;
}
function pubRuns(p) {
  const r = authorRuns(p.a);
  r.push(new TextRun(p.y ? ` (${p.y}) ` : " "));
  // title links to the publisher page where one exists; deliberately NOT styled
  // as a Hyperlink, so it stays black and unadorned in print but is clickable
  const url = D.links[p.t + " || " + p.j];
  if (url) r.push(new ExternalHyperlink({link: url, children: [new TextRun(`“${p.t}”`)]}), new TextRun(" "));
  else r.push(new TextRun(`“${p.t}” `));
  if (p.pre) r.push(new TextRun(p.pre));
  r.push(new TextRun({text: p.j, italics: true}));
  if (p.d === "forthcoming") r.push(new TextRun({text: ", ", }), new TextRun({text: "forthcoming", italics: true}), new TextRun("."));
  else if (p.d) r.push(new TextRun(` ${p.d}.`));
  else r.push(new TextRun("."));
  return r;
}
function wpRuns(w) {
  const r = authorRuns(w.a);
  r.push(new TextRun(` “${w.t}”`));
  if (w.s) r.push(new TextRun(" "), new TextRun({text: `(${w.s})`, italics: true}));
  return r;
}

// ---------- paragraph helpers ----------
function heading(text) {
  return new Paragraph({style: "CVHeading", children: [new TextRun(text)]});
}
function entry(children) {
  return new Paragraph({style: "CVEntry", children});
}
// label + tab, continuation lines aligned to COL
function dated(label, lines, style = "CVDated") {
  const kids = [new TextRun(label), new TextRun({children: [new Tab()]})];
  lines.forEach((l, i) => kids.push(new TextRun(i === 0 ? {text: l} : {text: l, break: 1})));
  return new Paragraph({style, children: kids});
}
function tight(text, extra = {}) {
  return new Paragraph({style: "CVTight", children: [new TextRun({text, ...extra})]});
}

// two-column borderless table (used for referee list + contact block)
function twoCol(leftKids, rightKids) {
  const cell = (kids) => new TableCell({
    width: {size: 4680, type: WidthType.DXA},
    margins: {top: 0, bottom: 0, left: 0, right: 0},
    children: kids,
    borders: {
      top: {style: BorderStyle.NONE}, bottom: {style: BorderStyle.NONE},
      left: {style: BorderStyle.NONE}, right: {style: BorderStyle.NONE},
    },
  });
  return new Table({
    columnWidths: [4680, 4680],
    width: {size: 9360, type: WidthType.DXA},
    borders: {
      top: {style: BorderStyle.NONE}, bottom: {style: BorderStyle.NONE},
      left: {style: BorderStyle.NONE}, right: {style: BorderStyle.NONE},
      insideHorizontal: {style: BorderStyle.NONE}, insideVertical: {style: BorderStyle.NONE},
    },
    rows: [new TableRow({children: [cell(leftKids), cell(rightKids)]})],
  });
}

// ---------- document body ----------
const body = [];

// masthead
body.push(new Paragraph({
  alignment: AlignmentType.RIGHT,
  spacing: {after: 60},
  border: {bottom: {style: BorderStyle.SINGLE, size: 8, color: "404040", space: 4}},
  children: [new TextRun({text: "Keaton S. Miller", size: 36, smallCaps: true, characterSpacing: 20})],
}));
body.push(new Paragraph({
  alignment: AlignmentType.RIGHT,
  spacing: {after: 200},
  children: [new TextRun({text: "Curriculum Vitae – September 8, 2026", size: 18, italics: true, color: "595959"})],
}));

// contact (phone removed)
// CVTight carries hanging: 360 for wrapped list entries. In here the left
// indent is 0, so an inherited hanging indent puts the first line at -360 --
// outside the cell, where Word clips it. Both have to be cleared.
const FLUSH = {left: 0, hanging: 0};
const addr = ["Department of Economics", "1285 University of Oregon", "Eugene, OR 97403-1285"]
  .map(t => new Paragraph({style: "CVTight", indent: FLUSH, children: [new TextRun(t)]}));
const reach = [
  new Paragraph({style: "CVTight", indent: FLUSH, alignment: AlignmentType.RIGHT, children: [
    new TextRun("Email: "),
    new ExternalHyperlink({link: "mailto:keatonm@uoregon.edu", children: [new TextRun({text: "keatonm@uoregon.edu", style: "Hyperlink"})]})]}),
  new Paragraph({style: "CVTight", indent: FLUSH, alignment: AlignmentType.RIGHT, children: [
    new TextRun("Website: "),
    new ExternalHyperlink({link: "https://keatonmiller.org", children: [new TextRun({text: "keatonmiller.org", style: "Hyperlink"})]})]}),
];
body.push(twoCol(addr, reach));
body.push(new Paragraph({spacing: {after: 0}, children: []}));

body.push(heading("Academic Positions"));
D.positions.forEach(([y, t]) => body.push(dated(y, [t])));

body.push(heading("Education"));
D.education.forEach(([y, lines]) => body.push(dated(y, lines)));

body.push(heading("Fields"));
body.push(entry([new TextRun(D.fields)]));

body.push(heading("Publications in Refereed Journals"));
D.journals.forEach(p => body.push(entry(pubRuns(p))));

body.push(heading("Contributions to Edited Volumes"));
D.chapters.forEach(p => body.push(entry(pubRuns(p))));

body.push(heading("Working Papers"));
D.working.forEach(w => body.push(entry(wpRuns(w))));

body.push(heading("Other Publications"));
D.other.forEach(p => body.push(entry(pubRuns(p))));

body.push(heading("Grants"));
D.grants.forEach(g => body.push(entry([
  new TextRun({text: g.role, bold: true}),
  new TextRun(`, ${g.src} (${g.yr}). `),
  new TextRun({text: g.t, italics: true}),
  new TextRun(`. ${g.amt}.`),
])));

body.push(heading("Presentations"));
D.presentations.forEach(([y, v]) => body.push(dated(y, v, "CVDatedTight")));

body.push(heading("Professional Referee Service"));
const half = Math.ceil(D.referee.length / 2);
body.push(twoCol(
  D.referee.slice(0, half).map(j => tight(j, {italics: true})),
  D.referee.slice(half).map(j => tight(j, {italics: true}))));
body.push(new Paragraph({style: "CVTight", keepNext: true, spacing: {before: 120}, children: [new TextRun({text: "Grant review", italics: true, bold: true})]}));
body.push(new Paragraph({style: "CVTight", spacing: {after: 130}, children: [new TextRun(D.grantReview.join("; ") + ".")]}));

body.push(heading("Department Service"));
D.deptService.forEach(([y, v]) => body.push(dated(y, v, "CVDatedTight")));

body.push(heading("University and External Service"));
D.univService.forEach(([y, v]) => body.push(dated(y, v, "CVDatedTight")));

body.push(heading("Teaching"));
D.teaching.forEach(([c, d]) => body.push(new Paragraph({
  style: "CVEntry",
  indent: {left: 1080, hanging: 720},
  children: [new TextRun(c), new TextRun({text: d, break: 1, italics: true, color: "404040"})],
})));

body.push(heading("Graduate Advising"));
body.push(new Paragraph({style: "CVTight", keepNext: true, children: [new TextRun({text: "Current students", italics: true, bold: true})]}));
D.currentStudents.forEach(s => body.push(tight(s)));
body.push(new Paragraph({style: "CVTight", keepNext: true, spacing: {before: 120}, children: [new TextRun({text: "Past students", italics: true, bold: true}), new TextRun({text: " (by role, then alphabetically, with initial placement)", italics: true})]}));
D.pastStudents.forEach(s => body.push(tight(s)));

body.push(heading("Undergraduate Advising"));
D.undergrad.forEach(s => body.push(tight(s)));

body.push(heading("Honors and Awards"));
D.honors.forEach(([y, v]) => body.push(dated(y, v, "CVDatedTight")));

// ---------- document ----------
const doc = new Document({
  creator: "Keaton Miller",
  lastModifiedBy: "Keaton Miller",
  title: "Keaton S. Miller – Curriculum Vitae",
  description: "Curriculum Vitae of Keaton S. Miller, Associate Professor of Economics, University of Oregon",
  styles: {
    default: {
      document: {run: {font: FONT, size: SZ}, paragraph: {spacing: {after: 120, line: 240}}},
    },
    paragraphStyles: [
      {id: "CVHeading", name: "CV Heading", basedOn: "Normal", next: "CVEntry", quickFormat: true,
       run: {font: FONT, size: 22, bold: true, smallCaps: true, characterSpacing: 12},
       paragraph: {spacing: {before: 280, after: 110}, keepNext: true, keepLines: true,
                   border: {bottom: RULE}, outlineLevel: 1}},
      {id: "CVEntry", name: "CV Entry", basedOn: "Normal", next: "CVEntry", quickFormat: true,
       run: {font: FONT, size: SZ},
       paragraph: {spacing: {after: 130}, indent: {left: 360, hanging: 360}, keepLines: true}},
      {id: "CVDated", name: "CV Dated Entry", basedOn: "Normal", next: "CVDated", quickFormat: true,
       run: {font: FONT, size: SZ},
       paragraph: {spacing: {after: 130}, indent: {left: COL, hanging: COL}, keepLines: true,
                   tabStops: [{type: TabStopType.LEFT, position: COL}]}},
      {id: "CVDatedTight", name: "CV Dated Entry Tight", basedOn: "CVDated", next: "CVDatedTight",
       paragraph: {spacing: {after: 110}, indent: {left: COL, hanging: COL}, keepLines: true,
                   tabStops: [{type: TabStopType.LEFT, position: COL}]}},
      {id: "CVTight", name: "CV Tight List", basedOn: "Normal", next: "CVTight", quickFormat: true,
       run: {font: FONT, size: SZ},
       // hanging indent so a wrapped entry cannot be mistaken for a new one
       paragraph: {spacing: {after: 0}, indent: {left: 720, hanging: 360}, keepLines: true}},
    ],
  },
  sections: [{
    properties: {
      page: {size: {width: 12240, height: 15840}, margin: {top: 1080, right: 1440, bottom: 1080, left: 1440}},
      titlePage: true,
    },
    headers: {
      first: new Header({children: [new Paragraph("")]}),
      default: new Header({children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        spacing: {after: 200},
        children: [new TextRun({text: "Keaton S. Miller – Curriculum Vitae – Page ", size: 18, italics: true, color: "595959"}),
                   new TextRun({children: [PageNumber.CURRENT], size: 18, italics: true, color: "595959"})],
      })]}),
    },
    children: body,
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(process.argv[2] || "out.docx", b);
  console.log("wrote", process.argv[2], b.length, "bytes");
});
