import regex
import sys
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
import html2markdown


COMBINED_NEWLINE_PATTERN = r"([^\S\n]*\n+[^\S\n]*)+"
COMPANY_TEXT_SUFFIX_PATTERN = r"\[[^\]]*\]\s*$"
DATE_DELIMITER_PATTERN = r"\s*\.\s*"
SOFT_WHITESPACE_PATTERN = r"[^\S\n]+"
WHITESPACE_PATTERN = r"\s+"

COMBINED_NEWLINE_REGEX = regex.compile(COMBINED_NEWLINE_PATTERN)
COMPANY_TEXT_SUFFIX_REGEX = regex.compile(COMPANY_TEXT_SUFFIX_PATTERN)
DATE_DELIMITER_REGEX = regex.compile(DATE_DELIMITER_PATTERN)
SOFT_WHITESPACE_REGEX = regex.compile(SOFT_WHITESPACE_PATTERN)
WHITESPACE_REGEX = regex.compile(WHITESPACE_PATTERN)


# region Elements
def get_position_page_rows(
    position_page: BeautifulSoup,
    print_warnings: bool = False,
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
        if print_warnings:
            print(
                "WARNING: Expected at least 1 position page table row, but got 0",
                file=sys.stderr,
            )

    rows = list()

    for table_row in table_rows:
        table_entries = table_row.find_all("td")

        if table_entries is None or len(table_entries) != 2:
            if print_warnings:
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
    text = html2markdown.convert(text)
    text = COMBINED_NEWLINE_REGEX.sub("\n", text)
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
    text = html2markdown.convert(text)
    text = COMBINED_NEWLINE_REGEX.sub("\n", text)
    text = text.strip()
    text = SOFT_WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_position_desc(position_desc: BeautifulSoup) -> str:
    text = position_desc.text
    text = html2markdown.convert(text)
    text = COMBINED_NEWLINE_REGEX.sub("\n", text)
    text = text.strip()
    text = SOFT_WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_competences(competences: BeautifulSoup) -> str:
    text = competences.text
    text = html2markdown.convert(text)
    text = COMBINED_NEWLINE_REGEX.sub("\n", text)
    text = text.strip()
    text = SOFT_WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_planned_start(
    planned_start: BeautifulSoup,
) -> Optional[Tuple[int, int, int]]:
    text = planned_start.text

    try:
        day, month, year = [
            int(x)
            for x in DATE_DELIMITER_REGEX.split(text)
            if x is not None and len(x) != 0
        ]
    except Exception:
        return None

    return year, month, day


def analyze_planned_end(
    planned_start: BeautifulSoup,
) -> Optional[Tuple[int, int, int]]:
    text = planned_start.text

    try:
        day, month, year = [
            int(x)
            for x in DATE_DELIMITER_REGEX.split(text)
            if x is not None and len(x) != 0
        ]
    except Exception:
        return None

    return year, month, day


def analyze_compensation(compensation: BeautifulSoup) -> str:
    text = compensation.text
    text = html2markdown.convert(text)
    text = text.strip()
    text = WHITESPACE_REGEX.sub(" ", text)

    return text


def analyze_location(location: BeautifulSoup) -> str:
    text = location.text
    text = html2markdown.convert(text)
    text = text.strip()
    text = WHITESPACE_REGEX.sub(" ", text)

    return text


TITLE_TO_KEYS = {
    "tvrtka": ("company_name", "company_url"),
    "opis tvrtke": "company_desc",
    "raspoloživih mjesta": "n_spots",
    "pozicija": "position_title",
    "opis": "position_desc",
    "kompetencije": "competences",
    "planirani početak": "planned_start",
    "planirani završetak": "planned_end",
    "honoriranje prakse": "compensation",
    "adresa prakse": "location",
}

TITLE_TO_FUNCTION = {
    "tvrtka": analyze_company,
    "opis tvrtke": analyze_company_description,
    "raspoloživih mjesta": analyze_n_spots,
    "pozicija": analyze_position,
    "opis": analyze_position_desc,
    "kompetencije": analyze_competences,
    "planirani početak": analyze_planned_start,
    "planirani završetak": analyze_planned_end,
    "honoriranje prakse": analyze_compensation,
    "adresa prakse": analyze_location,
}


def analyze_position_page_rows(
    position_page_rows: List[Tuple[BeautifulSoup, BeautifulSoup]]
) -> Dict[str, Any]:
    to_return = dict()

    for row in position_page_rows:
        label, content = row

        if label is None:
            raise RuntimeError("Couldn't parse position row label")

        if content is None:
            raise RuntimeError("Couldn't parse position row content")

        label = label.text
        label = label.strip()
        label = WHITESPACE_REGEX.sub(" ", label)
        label = label.lower()

        keys = TITLE_TO_KEYS[label]
        function = TITLE_TO_FUNCTION[label]

        if isinstance(keys, str):
            to_return[keys] = function(content)
        else:
            for key, result in zip(keys, function(content)):
                to_return[key] = result

    return to_return


# endregion
