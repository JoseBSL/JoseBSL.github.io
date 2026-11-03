
# ==========================================================
# Jose B. Lanuza | Academic Website
# Generate publications from BibTeX
# ==========================================================

from pathlib import Path
from html import escape
from urllib.parse import quote
import re
import unicodedata

from pybtex.database import parse_file
from pylatexenc.latex2text import LatexNodes2Text


# ==========================================================
# 1. Paths and bibliography
# ==========================================================

ROOT = Path(__file__).resolve().parent

BIB_FILE = ROOT / "publications.bib"
OUTPUT_FILE = ROOT / "publications-list.html"

bib = parse_file(str(BIB_FILE), bib_format="bibtex")

latex_converter = LatexNodes2Text()


# ==========================================================
# 2. Clean BibTeX text and accents
# ==========================================================

def clean(value):

    if value is None:
        return ""

    text = str(value)

    # Convert LaTeX accents and special characters
    text = latex_converter.latex_to_text(text)

    # Normalize typography
    text = text.replace("---", "—")
    text = text.replace("--", "–")
    text = text.replace("``", "“")
    text = text.replace("''", "”")

    # Normalize Unicode accents
    text = unicodedata.normalize("NFC", text)

    # Remove unnecessary whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# 3. Author formatting
# ==========================================================

MY_NAME = '<strong class="my-name">JB Lanuza</strong>'


def author_name(person):

    first = clean(" ".join(
        person.first_names + person.middle_names
    ))

    last = clean(" ".join(
        person.prelast_names + person.last_names
    ))

    full = f"{first} {last}".strip()

    # Standardize your name
    if re.search(r"\bLanuza\b", full, re.IGNORECASE):
        return MY_NAME

    return escape(full)


def format_authors(persons):

    # Preserve all authors in their actual order
    names = [
        author_name(person)
        for person in persons
    ]

    return ", ".join(names)


# ==========================================================
# 4. Publication year
# ==========================================================

def year_of(entry):

    value = clean(entry.fields.get("year", ""))

    match = re.search(
        r"\b(?:19|20)\d{2}\b",
        value
    )

    return int(match.group()) if match else 0


# ==========================================================
# 5. Journal reference formatting
# ==========================================================

def format_journal(fields):

    journal = escape(clean(
        fields.get(
            "journal",
            fields.get("journaltitle", "")
        )
    ))

    volume = escape(clean(
        fields.get("volume", "")
    ))

    number = escape(clean(
        fields.get("number", "")
    ))

    pages = escape(clean(
        fields.get(
            "pages",
            fields.get("eid", "")
        )
    ))

    details = []

    if journal:
        details.append(f"<em>{journal}</em>")

    if volume:

        volume_text = volume

        if number:
            volume_text += f"({number})"

        details.append(volume_text)

    elif number:
        details.append(f"({number})")

    if pages:
        details.append(pages)

    return ", ".join(details) + "." if details else ""


# ==========================================================
# 6. DOI formatting
# ==========================================================

def doi_url(fields):

    doi = clean(fields.get("doi", "")).strip()

    if not doi:
        return None

    # Remove DOI URL prefixes
    doi = re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        doi,
        flags=re.IGNORECASE
    )

    # Remove optional DOI prefix
    doi = re.sub(
        r"^doi:\s*",
        "",
        doi,
        flags=re.IGNORECASE
    )

    doi = doi.strip().rstrip("/")

    if not doi:
        return None

    # Encode unsafe URL characters
    doi = quote(doi, safe="/:;()-.~_")

    return f"https://doi.org/{doi}"


# ==========================================================
# 7. External-link SVG icon
# ==========================================================

EXTERNAL_LINK_ICON = """
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
>
    <path d="M15 3h6v6"/>
    <path d="M10 14 21 3"/>
    <path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"/>
</svg>
"""


# ==========================================================
# 8. Format each publication
# ==========================================================

def format_entry(entry):

    fields = entry.fields

    title = escape(clean(
        fields.get("title", "Untitled")
    )).rstrip(". ")

    authors = format_authors(
        entry.persons.get("author", [])
    )

    journal = format_journal(fields)

    link = doi_url(fields)

    parts = []

    # Authors
    if authors:
        parts.append(f"{authors}.")

    # Article title: regular weight, not clickable
    parts.append(
        f'<span class="publication-title">'
        f'{title}.'
        f'</span>'
    )

    # Journal information
    if journal:
        parts.append(journal)

    # DOI link with classic external-link icon
    if link:

        doi_html = (
            f'<a class="publication-doi" '
            f'href="{escape(link, quote=True)}" '
            f'target="_blank" '
            f'rel="noopener noreferrer" '
            f'aria-label="Open publication DOI">'
            f'DOI '
            f'{EXTERNAL_LINK_ICON}'
            f'</a>'
        )

        parts.append(doi_html)

    reference = " ".join(parts)

    return (
        '<article class="publication-entry">\n'
        f'  <div class="publication-reference">'
        f'{reference}</div>\n'
        '</article>'
    )


# ==========================================================
# 9. Sort publications by year (newest first)
# ==========================================================

entries = sorted(
    bib.entries.values(),
    key=year_of,
    reverse=True
)


# ==========================================================
# 10. Generate HTML grouped by year
# ==========================================================

output = ['<div class="publications-list">']

current_year = None

for entry in entries:

    year = year_of(entry)

    if year != current_year:

        current_year = year

        label = str(year) if year else "Undated"

        output.append(
            f'<h3 class="publication-year">'
            f'{label}'
            f'</h3>'
        )

    output.append(format_entry(entry))

output.append("</div>")


# ==========================================================
# 11. Save HTML
# ==========================================================

OUTPUT_FILE.write_text(
    "\n".join(output),
    encoding="utf-8"
)


# ==========================================================
# 12. Summary
# ==========================================================

n_publications = len(entries)

n_doi = sum(
    bool(doi_url(entry.fields))
    for entry in entries
)

print(
    f"Generated {n_publications} publications "
    f"in {OUTPUT_FILE.name}"
)

print(
    f"Publications with DOI links: {n_doi}"
)

print(
    f"Publications without DOI links: "
    f"{n_publications - n_doi}"
)
