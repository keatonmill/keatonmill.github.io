"""Post-render fixup: Quarto emits about-page buttons with root-absolute
hrefs (e.g. href="/research.html"), which break when the site is served
from a subpath such as username.github.io/repo/. Rewrite them relative."""

import re
from pathlib import Path

for page in Path("_site").glob("*.html"):
    html = page.read_text()
    fixed = re.sub(r'(<a href=")/(?!/)', r"\1./", html)
    if fixed != html:
        page.write_text(fixed)
        print(f"fix-links: rewrote absolute hrefs in {page}")
