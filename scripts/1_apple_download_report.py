import os, sys
import pathlib
import datetime

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

RELEASES_PATH = f"{APP_PATH}/../data-input/apple-mobility"

api_revision = (datetime.datetime.now() - datetime.datetime(datetime.datetime.now().year, 9, 12)).days
# 38 on 23 or May 2020

link = f"https://covid19-static.cdn-apple.com/covid19-mobility-data/2017HotfixDev{api_revision}/v3/en-us/applemobilitytrends-"


def download_csv(date_report):
    call = (
        f"curl -f -o {RELEASES_PATH}/applemobilitytrends-{date_report}.csv -L "
        f"{link}"
        f"{date_report}.csv"
    )
    print(call)
    output = os.system(call)
    if output != 0:
        raise Exception("Failed Download")


if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta

    date_yesterday = (datetime.now().date() - timedelta(days=2)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--date", default=date_yesterday, help="Report Date: YYYY-MM-DD",
    )

    args = parser.parse_args()
    date = args.date

    print(f"Downloading Report for {date}")
    download_csv(date)
