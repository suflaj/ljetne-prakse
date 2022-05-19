import argparse
from getpass import getpass
import multiprocessing
from pathlib import Path
import os
import sys
import traceback
from typing import Tuple

from bs4 import BeautifulSoup
from tqdm import tqdm

from ljetne_prakse.scraping.auth import login_to_fer
from ljetne_prakse.scraping.main_page import get_main_page_rows, analyze_main_page_rows

# from ljetne_prakse.utils.paths import DEFAULT_DATA_FOLDER
from ljetne_prakse.utils.time import get_timestamp

DEFAULT_DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"


def get_arguments(args) -> Tuple[str, Path, Path, Path, int]:
    url = str(args.url).strip()

    if args.destination_folder is None:
        destination_folder = Path(DEFAULT_DATA_FOLDER / get_timestamp())
    else:
        destination_folder = Path(args.destination_folder)

    main_page_name = str(args.main_page_name).strip()
    main_page_path = destination_folder / main_page_name

    secondary_pages_folder_name = str(args.secondary_pages_folder_name)
    secondary_pages_folder = destination_folder / secondary_pages_folder_name

    n_processes = args.n_processes
    if n_processes is None or n_processes < 1:
        n_processes = multiprocessing.cpu_count()
    n_processes = int(n_processes)

    return url, destination_folder, main_page_path, secondary_pages_folder, n_processes


def process_page(args):
    session, href, destination = args

    # Timeout is useless, FER throttles requests
    position_page = session.get(href)

    if position_page is None or position_page.status_code != 200:
        print(f"WARNING: Couldn't fetch `{href}`, skipping")
        return

    page_text = BeautifulSoup(position_page.text, "html.parser").prettify()

    with open(
        destination,
        mode="w+",
        encoding="utf8",
        errors="replace",
    ) as f:
        f.write(page_text)


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

    parser.add_argument(
        "--n_processes",
        "-n",
        type=int,
        default=-1,
        help=(
            "The number of processes to run while fetching sites. -1 is for the number "
            "of cores"
        ),
    )

    args = parser.parse_args()

    # endregion

    (
        url,
        destination_folder,
        main_page_path,
        secondary_pages_folder,
        n_processes,
    ) = get_arguments(args=args)
    print(
        f"URL: {url}\n"
        f"Destination HTML path: {main_page_path}\n"
        f"Secondary pages folder: {secondary_pages_folder}\n"
        f"Number of processes: {n_processes}\n"
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

        print("Analyzing main pagye")
        main_page_rows = get_main_page_rows(main_page=soup)
        print(f"Found {len(main_page_rows)} main page rows")
        parsed_rows = analyze_main_page_rows(main_page_rows=main_page_rows)
        hrefs = [
            f"https://www.fer.unizg.hr{row['url']}"
            for row in parsed_rows
            if row is not None and "url" in row
        ]

        print("Saving position pages")
        if not os.path.exists(secondary_pages_folder):
            os.makedirs(secondary_pages_folder)

        iterator = tqdm(
            range(len(hrefs)), desc="Processing pages", file=sys.stdout, ncols=80
        )
        with multiprocessing.Pool(n_processes) as pool:
            sessions = [session] * len(hrefs)
            destinations = [
                secondary_pages_folder / f"page-{i}.html" for i in range(len(hrefs))
            ]

            for _ in pool.imap_unordered(
                process_page, iterable=zip(sessions, hrefs, destinations)
            ):
                iterator.update()


if __name__ == "__main__":
    main()
