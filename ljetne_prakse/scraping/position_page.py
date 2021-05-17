import regex
import sys
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup


COMPANY_TEXT_SUFFIX_PATTERN = r"\[[^\]]*\]\s*$"
SOFT_WHITESPACE_PATTERN = r"[^\S\n]+"
WHITESPACE_PATTERN = r"\s+"


COMPANY_TEXT_SUFFIX_REGEX = regex.compile(COMPANY_TEXT_SUFFIX_PATTERN)
SOFT_WHITESPACE_REGEX = regex.compile(SOFT_WHITESPACE_PATTERN)
WHITESPACE_REGEX = regex.compile(WHITESPACE_PATTERN)


# region Elements
def get_position_page_rows(
    position_page: BeautifulSoup,
) -> List[Tuple[BeautifulSoup, BeautifulSoup]]:
    root = position_page.find("div", class_="fer_ljetna_praksa")

    if root is None:
        raise RuntimeError("Couldn't parse position page root")

    table = root.find("table")

    if table is None:
        raise RuntimeError("Couldn't parse position page table")

    table_rows = table.find_all("tr")

    if table_rows is None:
        raise RuntimeError("Couldn't parse position page table rows")

    if len(table_rows) == 0:
        print(
            "WARNING: Expected at least 1 position page table row, but got 0",
            file=sys.stderr,
        )

    rows = list()

    for table_row in table_rows:
        table_entries = table_row.find_all("td")

        if table_entries is None or len(table_entries) != 2:
            print("WARNING: Encountered empty or non-2-long row, skipping...")
            continue

        rows.append(tuple(table_entries))

    return rows


# endregion

# region Analysis


def analyze_company(company: BeautifulSoup) -> Tuple[str, Optional[str]]:
    text = company.text
    text = COMPANY_TEXT_SUFFIX_REGEX.sub("", text)
    text = text.strip()
    text = WHITESPACE_REGEX.sub(" ", text)

    anchor = company.find("a")
    href = None if anchor is None else anchor.get("href")

    if href is not None:
        href = str(href).strip()
        href = WHITESPACE_REGEX.sub(" ", href)
        href = href.lower()

    return text, href


def analyze_company_description(company_description: BeautifulSoup) -> str:
    text = company_description.text
    text = COMPANY_TEXT_SUFFIX_REGEX.sub("", text)
    text = text.strip()
    text = SOFT_WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_n_spots(n_spots: BeautifulSoup) -> str:
    text = n_spots.text
    text = text.strip()
    text = WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_position(position: BeautifulSoup) -> str:
    text = position.text
    text = text.strip()
    text = WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_position_desc(position_desc: BeautifulSoup) -> str:
    # TODO: Convert HTML to Markdown
    pass


TITLE_TO_FUNCTION = {
    "tvrtka": analyze_company,
    "opis tvrtke": analyze_company_description,
    "raspoloživih mjesta": analyze_n_spots,
    "pozicija": analyze_position,
    "opis": analyze_position_desc,
    "kompetencije": None,
    "planirani početak": None,
    "planirani završetak": None,
    "honoriranje prakse": None,
    "adresa prakse": None,
}


def analyze_position_page_rows(
    position_page_rows: List[Tuple[BeautifulSoup, BeautifulSoup]]
) -> Dict[str, Any]:
    pass


# endregion
