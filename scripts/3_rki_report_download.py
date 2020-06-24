import os

# import dotenv
# dotenv.load_dotenv(verbose=True)
# RELEASES_PATH = os.getenv("RELEASES_PATH")
import pathlib
import sys

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

RELEASES_PATH = f"{APP_PATH}/../data-input/rki-reports"


def download_csv(date_report, language="en"):
    call = (
        f"curl -f -o {RELEASES_PATH}/{date_report}-{language}.pdf -L "
        "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Situationsberichte/"
        f"{date_report}-{language}.pdf?__blob=publicationFile"
    )
    print(call)
    output = os.system(call)
    if output != 0:
        raise Exception("Failed Download")


if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta

    date_yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--language",
        default="en",
        help="Report language: en for English, de for German",
    )
    parser.add_argument(
        "--date", default=date_yesterday, help="Report Date: YYYY-MM-DD",
    )

    args = parser.parse_args()
    date = args.date
    language = args.language

    print(f"Downloading Report in {language} for {date}")
    download_csv(date, language=language)
