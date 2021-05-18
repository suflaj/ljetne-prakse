import argparse
from getpass import getpass
from pathlib import Path
import os
import sys
import traceback
from typing import Tuple

from bs4 import BeautifulSoup
from tqdm import tqdm

from ljetne_prakse.scraping.auth import login_to_fer
from ljetne_prakse.scraping.main_page import get_main_page_rows, analyze_main_page_rows
from ljetne_prakse.utils.paths import DEFAULT_DATA_FOLDER
from ljetne_prakse.utils.time import get_timestamp


def get_arguments(args) -> Tuple[str, Path]:
    url = str(args.url).strip()

    if args.destination_folder is None:
        destination_folder = Path(DEFAULT_DATA_FOLDER / get_timestamp())
    else:
        destination_folder = Path(args.destination_folder)

    main_page_name = str(args.main_page_name).strip()
    main_page_path = destination_folder / main_page_name

    secondary_pages_folder_name = str(args.secondary_pages_folder_name)
    secondary_pages_folder = destination_folder / secondary_pages_folder_name

    return url, destination_folder, main_page_path, secondary_pages_folder


def main():
    # region Parsing
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        "-u",
        type=str,
        default="https://www.fer.unizg.hr/prakse/prijava",
        help="A str representing the URL of the main practice page.",
    )

    parser.add_argument(
        "--destination_folder",
        "-f",
        type=str,
        default=None,
        help="A str representing the path to the destination folder.",
    )

    parser.add_argument(
        "--main_page_name",
        "-m",
        type=str,
        default="main.html",
        help="A str representing the file name of the main page file.",
    )

    parser.add_argument(
        "--secondary_pages_folder_name",
        "-s",
        type=str,
        default="position-pages",
        help="A str representing the folder name of the secondary files.",
    )

    args = parser.parse_args()

    # endregion

    url, destination_folder, main_page_path, secondary_pages_folder = get_arguments(
        args=args
    )

    while True:
        try:
            username = input("Username: ")
            password = getpass("Password: ")

            session = login_to_fer(username=username, password=password)
            break
        except RuntimeError:
            print(f"Login failed because: {traceback.format_exc()}", file=sys.stderr)

    print(f"\nSuccessfully logged in as {username}!\n")

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    print("Getting main page...")
    main_page = session.get(url)

    if main_page is not None and main_page.status_code == 200:
        print("Parsing main page")
        soup = BeautifulSoup(main_page.text, "html.parser")
        soup_text = soup.prettify()

        print("Saving main page")
        with open(main_page_path, mode="w+", encoding="utf8", errors="replace") as f:
            f.write(str(soup_text).strip())

        print("Analyzing main page")
        main_page_rows = get_main_page_rows(main_page=soup)
        parsed_rows = analyze_main_page_rows(main_page_rows=main_page_rows)
        hrefs = [
            f"https://www.fer.unizg.hr{row['url']}"
            for row in parsed_rows
            if row is not None and "url" in row
        ]

        print("Saving position pages")
        if not os.path.exists(secondary_pages_folder):
            os.makedirs(secondary_pages_folder)

        for i, href in tqdm(
            enumerate(hrefs),
            desc="Saving position pages",
            total=len(hrefs),
            file=sys.stdout,
        ):
            position_page = session.get(href)

            if position_page is None or position_page.status_code != 200:
                print(f"WARNING: Couldn't fetch `{href}`, skipping")
                continue

            page_text = BeautifulSoup(position_page.text, "html.parser").prettify()

            with open(
                secondary_pages_folder / f"page-{i}.html",
                mode="w+",
                encoding="utf8",
                errors="replace",
            ) as f:
                f.write(page_text)


if __name__ == "__main__":
    main()
