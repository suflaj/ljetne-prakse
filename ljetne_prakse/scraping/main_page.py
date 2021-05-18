import regex
import sys
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

COMPANY_TEXT_SUFFIX_PATTERN = r"\[[^\]]*\]\s*$"
WHITESPACE_PATTERN = r"\s+"

COMPANY_TEXT_SUFFIX_REGEX = regex.compile(COMPANY_TEXT_SUFFIX_PATTERN)
WHITESPACE_REGEX = regex.compile(WHITESPACE_PATTERN)


# region Elements
def get_main_page_table(main_page: BeautifulSoup):
    root = main_page.find("div", class_="fer_ljetna_praksa")

    if root is None:
        raise RuntimeError("Couldn't parse main page root")

    tables = root.find_all("table")

    if len(tables) < 2:
        raise RuntimeError("Couldn't parse main page tables")
    elif len(tables) != 2:
        print(
            f"WARNING: Found {len(tables)} tables, expected 2",
            file=sys.stderr,
        )

    table = tables[1]

    if table is None:
        raise RuntimeError("Coulnd't parse main page table")

    return table


def get_main_page_rows(main_page: BeautifulSoup):
    table = get_main_page_table(main_page=main_page)

    table_rows = table.find_all("tr")

    if table_rows is None:
        raise RuntimeError("Couldn't parse main page rows")

    if len(table_rows) == 0:
        print(
            "WARNING: Expected at least 1 main page table row, but got 0",
            file=sys.stderr,
        )

    rows = list()

    for table_row in table_rows:
        table_entries = table_row.find_all("td")

        if table_entries is None or len(table_entries) != 4:
            print("WARNING: Encountered empty or non-4-long row, skipping...")
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


def analyze_action(action: BeautifulSoup) -> Optional[str]:
    anchor = action.find("a", class_="button")

    href = None if anchor is None else anchor.get("href")

    if href is not None:
        href = str(href).strip()
        href = WHITESPACE_REGEX.sub(" ", href)

    return href


def analyze_main_page_rows(
    main_page_rows: List[
        Tuple[BeautifulSoup, BeautifulSoup, BeautifulSoup, BeautifulSoup]
    ]
) -> List[Dict[str, str]]:
    result = list()

    for company, n_spots, position, action in main_page_rows:
        company_text, company_url = analyze_company(company=company)
        n_spots_text = analyze_n_spots(n_spots=n_spots)
        position_text = analyze_position(position=position)
        action_url = analyze_action(action=action)

        result.append(
            {
                "company": company_text,
                "company_url": company_url,
                "n_spots": n_spots_text,
                "position": position_text,
                "url": action_url,
            }
        )

    return result


# endregion
