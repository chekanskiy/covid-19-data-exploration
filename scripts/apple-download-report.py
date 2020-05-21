import os, sys
import pathlib


APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

RELEASES_PATH = f'{APP_PATH}/../data-input/apple-mobility'

link = f"https://covid19-static.cdn-apple.com/covid19-mobility-data/2008HotfixDev36/v3/en-us/applemobilitytrends-"
report_date = '2020-05-17'


def download_csv(date_report):
    call = (
        f"curl -f -o {RELEASES_PATH}/applemobilitytrends-{date_report}.csv -L "
        f"{link}"
        f"{date_report}.csv"
    )
    print(call)
    os.system(call)


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

    print(f'Downloading Report for {date}')
    download_csv(date)
