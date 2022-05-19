import argparse
import json
import os
from pathlib import Path
import regex
import sys
from typing import Tuple

from bs4 import BeautifulSoup
from tqdm import tqdm
import unidecode

from ljetne_prakse.scraping.position_page import (
    analyze_position_page_rows,
    get_position_page_rows,
)

# from ljetne_prakse.utils.paths import DEFAULT_DATA_FOLDER

DEFAULT_DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"

NON_WORD_PATTERN = r"[^\w\s]+"
WHITESPACE_PATTERN = r"\s+"

NON_WORD_REGEX = regex.compile(NON_WORD_PATTERN)
WHITESPACE_REGEX = regex.compile(WHITESPACE_PATTERN)


def get_arguments(args) -> Tuple[Path, Path, str, bool]:
    if args.source_folder is None:
        root = DEFAULT_DATA_FOLDER

        folders = [root / folder_name for folder_name in os.listdir(root)]
        folders = [folder for folder in folders if os.path.isdir(folder)]

        if len(folders) == 0:
            raise RuntimeError(
                f"Couldn't find scraped data in {root}. Make sure you run "
                "`get_pages.py` before this."
            )

        folders = sorted(folders)
        most_recent_folder = folders[-1]
        source_folder = most_recent_folder / "position-pages"
    else:
        source_folder = Path(args.source_folder)

    if args.destination_folder is None:
        destination_folder = source_folder.parent / "analysis"
    else:
        destination_folder = Path(args.destination_folder)

    results_name = str(args.results_name).strip()
    save_separately = bool(args.save_separately)

    return source_folder, destination_folder, results_name, save_separately


def normalize_for_file_name(text: str):
    new_text = text.strip()
    new_text = unidecode.unidecode(new_text)
    new_text = NON_WORD_REGEX.sub("", new_text)
    new_text = WHITESPACE_REGEX.sub("-", new_text)
    new_text = new_text.lower()

    return new_text


def main():
    # region Parsing
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source_folder",
        "-s",
        type=str,
        default=None,
        help="A str representing the folder where the position page HTMLs are located",
    )

    parser.add_argument(
        "--destination_folder",
        "-f",
        type=str,
        default=None,
        help="A str representing the folder where the analysis results will be saved",
    )

    parser.add_argument(
        "--results_name",
        "-r",
        type=str,
        default="results.json",
        help=(
            "A str representing the file name of the results file (ignored if "
            "--save_separately is set)"
        ),
    )

    parser.add_argument(
        "--save_separately",
        action="store_true",
        help="A flag; if set, results will be saved separately for each company.",
    )

    args = parser.parse_args()

    # region endregion

    source_folder, destination_folder, results_name, save_separately = get_arguments(
        args=args
    )

    print("Getting file paths")
    file_paths = [source_folder / file_name for file_name in os.listdir(source_folder)]
    file_paths = [
        file_path
        for file_path in file_paths
        if os.path.isfile(file_path) and str(file_path).endswith(".html")
    ]

    print("Sorting file paths")
    file_paths = sorted(file_paths)

    if len(file_paths) == 0:
        raise RuntimeError(f"Couldn't find position pages in {source_folder}")

    print("Reading position pages")
    results = list()

    for file_path in tqdm(file_paths, desc="Analyzing position pages", file=sys.stdout):
        with open(file_path, encoding="utf8", errors="replace") as f:
            position_page = f.read()

        soup = BeautifulSoup(position_page, "html.parser")

        if soup is None:
            print(
                f"WARNING: Couldn't parse position page in {file_path}, skipping",
                file=sys.stderr,
            )
            continue

        position_page_rows = get_position_page_rows(position_page=soup)

        if position_page_rows is None or len(position_page_rows) == 0:
            print(
                f"WARNING: Couldn't parse position page rows in {file_path}, skipping",
                file=sys.stderr,
            )
            continue

        result = analyze_position_page_rows(position_page_rows=position_page_rows)

        if result is not None:
            results.append(result)

    print("Regrouping position pages")
    regrouped_results = dict()

    for result in results:
        company_name = result["company_name"]

        if company_name not in regrouped_results:
            regrouped_results[company_name] = list()

        del result["company_name"]

        regrouped_results[company_name].append(result)

    print("Saving results")
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    if save_separately:
        destination_folder = destination_folder / "companies"

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for company_name, results in tqdm(
            regrouped_results.items(), desc="Saving results", file=sys.stdout
        ):
            file_name = normalize_for_file_name(company_name) + ".json"

            with open(
                destination_folder / file_name,
                mode="w+",
                encoding="utf8",
                errors="replace",
            ) as f:
                json.dump(
                    results,
                    f,
                    skipkeys=False,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=False,
                )
    else:
        with open(
            destination_folder / results_name,
            mode="w+",
            encoding="utf8",
            errors="replace",
        ) as f:
            json.dump(
                regrouped_results,
                f,
                skipkeys=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,
            )


if __name__ == "__main__":
    main()
