from tabula import read_pdf, read_pdf_with_template
from tabulate import tabulate
import datetime
import pandas as pd
import numpy as np
import pathlib
import sys

import warnings

warnings.simplefilter("ignore")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)


def select_template(date, APP_PATH):
    if date <= "2020-03-04":
        return f"{APP_PATH}/templates/2020-03-04-en.tabula-template.json"
    elif date <= "2020-03-07":
        return f"{APP_PATH}/templates/2020-03-06-en.tabula-template.json"
    elif date <= "2020-03-08":
        return f"{APP_PATH}/templates/2020-03-08-en.tabula-template.json"
    elif date <= "2020-03-09":
        return f"{APP_PATH}/templates/2020-03-09-en.tabula-template.json"
    elif date <= "2020-03-10":
        return f"{APP_PATH}/templates/2020-03-10-en.tabula-template.json"
    elif date <= "2020-03-11":
        return f"{APP_PATH}/templates/2020-03-11-en.tabula-template.json"
    elif date <= "2020-03-14":
        return f"{APP_PATH}/templates/2020-03-12-en.tabula-template.json"
    elif date <= "2020-03-16":
        return f"{APP_PATH}/templates/2020-03-15-en.tabula-template.json"
    elif date <= "2020-03-18":
        return f"{APP_PATH}/templates/2020-03-17-en.tabula-template.json"
    elif date <= "2020-03-19":
        return f"{APP_PATH}/templates/2020-03-19-en.tabula-template.json"
    elif date <= "2020-03-21":
        return f"{APP_PATH}/templates/2020-03-20-en.tabula-template.json"
    elif date <= "2020-03-22":
        return f"{APP_PATH}/templates/2020-03-22-en.tabula-template.json"
    elif date <= "2020-03-23":
        return f"{APP_PATH}/templates/2020-03-23-en.tabula-template.json"
    elif date <= "2020-03-24":
        return f"{APP_PATH}/templates/2020-03-24-en.tabula-template.json"
    elif date <= "2020-05-19":
        return f"{APP_PATH}/templates/2020-05-18-en.tabula-template.json"
    elif date <= "2020-05-21":
        return f"{APP_PATH}/templates/2020-05-20-en.tabula-template.json"
    elif date <= "2020-05-22":
        return f"{APP_PATH}/templates/2020-05-22-en.tabula-template.json"
    elif date <= "2020-05-23":
        return f"{APP_PATH}/templates/2020-05-23-en.tabula-template.json"
    elif date <= "2020-05-24":
        return f"{APP_PATH}/templates/2020-05-24-en.tabula-template.json"
    else:
        return f"{APP_PATH}/templates/2020-05-25-en.tabula-template.json"


def extract_text(l):
    return "".join(
        [k for k in l if not k.isdigit() and not k in [".", ",", "+"]]
    ).rstrip()


def count_numbers(l):
    c = 0
    try:
        c += sum([1 for k in str(l) if k.isdigit()])
        return c
    except:
        return c


def extract_number(l):
    def fix_string(l):
        l = "".join([k for k in l if k.isdigit() is True]).lstrip().rstrip()
        return l

    if type(l) == str:
        result = fix_string(l.values[0])
        if len(result) > 0:
            return int(result)
        else:
            return 0
    else:
        try:
            result = l.fillna(0).values[0]
        except:
            result = l.fillna(0).values
        try:
            result = round(result, 3)
        except:
            pass
        if "." in str(result):
            if len(str(result).split(".")[1]) > 2:
                result = int(fix_string(str(result)).replace(".", ""))
                return result
        elif "," in str(result):
            if len(str(result).split(",")[1]) > 2:
                result = int(fix_string(str(result)).replace(",", ""))
                return result
        return int(fix_string(str(result)))


def fix_misaligned_row(df):
    land_first_names = [
        "Mecklenburg-",
        "Mecklenburg-Western",
        "Baden-",
        "Baden-Wuerttemberg",
        "North Rhine-",
        "Rhineland-",
        "Rhineland-Palatinate",
        "Saxony-",
        "Saxony-Anhalt",
        "Schleswig-",
        "Schleswig-Holstein",
        "Lower",
        "Lower Saxony",
        "Sachsen-",
    ]
    land_second_names = [
        "Wuerttemberg",
        "Pomerania",
        "Western Pomerania",
        "Saxony",
        "Westphalia",
        "Palatinate",
        "Anhalt",
        "Holstein",
        "-",
    ]
    land_single_word_names = ["Bavaria", 'Berlin', 'Brandenburg', 'Bremen', 'Bremen*',
                              'Hamburg', 'Saarland', 'Thuringia', 'Hesse', 'Saxony']
    df = df.reset_index(drop=True)
    for row in df.itertuples():
        # if land is not empty and values are null and land is not the beginning of other names
        row_index = row[0]
        row_index_plus1 = row_index + 1
        row_index_plus2 = row_index + 2
        if (
                str(row.land) != "nan"
                and str(row.land).strip().replace("*", "") in set(land_first_names + land_single_word_names)
                and pd.isnull(row[2]) is True
        ):
            print('Clause 1', str(row.land))
            if (
                    str(df.loc[row_index_plus1, "land"]).replace("*", "")
                    not in set(land_first_names + land_single_word_names)
            ):
                print('Clause 2', str(row.land))
                df.loc[row_index, "land"] = (
                        (str(row.land).replace("nan", "")).strip()
                        + " "
                        + str(df.loc[row_index_plus1, "land"])
                        .strip()
                        .replace("nan", "")
                )
                if pd.isnull(df.loc[row_index_plus1, df.columns[2]]) is False:
                    print('Taking next row', str(row.land))
                    df.loc[row_index, df.columns[1:]] = df.loc[
                        row_index_plus1, df.columns[1:]
                    ]
                    df.drop(axis=1, index=row_index_plus1, inplace=True)
                else:
                    print('Taking next row + 1', str(row.land))
                    df.loc[row_index, df.columns[1:]] = df.loc[
                        row_index_plus2, df.columns[1:]
                    ]
                    df.drop(axis=1, index=row_index_plus2, inplace=True)
    return df


def load_pdf(date, path, lang="en"):
    path += "{0}-{1}.pdf".format(date, lang)
    if date <= "2020-05-27":
        template = select_template(date, APP_PATH)
        print(path, "\n", template)
        dfs = read_pdf_with_template(
            path, pandas_options={"header": None, "dtype": str}, template_path=template
        )
    else:
        # fmt: off
        if date <= "2020-05-28":
            area = [304, 69, 674, 547]  # Points: Top Y, Left X, Bottom Y, Right X
            columns = [160, 205, 254, 319, 370, 432, 476, ]  # Points: X coordinates of column splits

        elif date <= "2020-06-01":
            area = [304, 69, 816, 547]  # Points: Top Y, Left X, Bottom Y, Right X
            columns = [160, 205, 254, 319, 370, 432, 476, ]  # Points: X coordinates of column splits
        else:
            area = [86, 69, 820, 547]  # Points: Top Y, Left X, Bottom Y, Right X
            columns = [158, 205, 254, 319, 370, 432, 476,]  # Points: X coordinates of column splits
        dfs = read_pdf(
            path,
            pandas_options={"header": None, "dtype": str},
            stream=True,
            pages=3,
            area=area,
            columns=columns,
        )
    # fmt: on
    print(dfs, "\n" * 2)
    df = dfs[0]
    if len(df.columns) == 2:
        print("Extracting 2 data columns")
        df.columns = ["land", "confirmed"]
        df = df.loc[:, ["land", "confirmed"]]
    elif len(df.columns) == 4:
        if date > "2020-03-24":
            print("Extracting 4 data columns after '2020-03-24'")
            df.columns = ["land", "confirmed", "daily", "dead"]
            df["per_mil"] = 0
            df = df.loc[:, ["land", "confirmed", "daily", "per_mil", "dead"]]
        else:
            print("Extracting 4 data columns before '2020-03-24'")
            df.columns = ["land", "confirmed", "electronically_submitted", "per_100k"]
            df["per_mil"] = 0
            df = df.loc[:, ["land", "confirmed"]]
    elif len(df.columns) == 5:
        print("Extracting 5 data columns")
        df.columns = ["land", "confirmed", "daily", "per_mil", "dead"]
    elif len(df.columns) == 6:
        print("Extracting 6 data columns")
        df.columns = ["land", "confirmed", "daily", "per_mil", "dead", "dead_per_100k"]
    elif len(df.columns) == 8:
        print("Extracting 6 data columns")
        df.columns = [
            "land",
            "confirmed",
            "daily",
            "per_mil",
            "7day_sum",
            "7day_100k",
            "dead",
            "dead_per_100k",
        ]
    else:
        print(f"Falied to exctract {len(df.columns)} data columns")
        print(df.head(20))
        raise Exception
    df = fix_misaligned_row(df)

    # Replace with a clause: if all columns except land contain numbers
    df["c"] = df.loc[:, "confirmed"].apply(count_numbers)
    df["d"] = df.loc[:, "dead"].apply(count_numbers)
    df = df.loc[(df.c != 0) & (df.d != 0), :]

    df.loc[:, ["confirmed"]] = df.loc[:, ["confirmed"]].apply(extract_number, axis=1)
    if "dead" in df.columns:
        df.loc[:, ["dead"]] = df.loc[:, ["dead"]].apply(extract_number, axis=1)
    else:
        df["dead"] = 0
    df = df.loc[
         (df.land.str.contains("cases") == False)
         & (df.land.str.contains("Total") == False)
         & (df.land.str.contains("total") == False)
         & (df.land.str.contains("Gesamt") == False)
         & (df.land.str.contains("gesamt") == False),
         :,
         ]
    try:
        df["date"] = datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        df["date"] = date
    df = df.loc[:, ["land", "confirmed", "dead", "date"]]
    return df.reset_index(drop=True)


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

    # =========================================== LOADING AND PARSING REPORT ======================================
    df_new = load_pdf(
        date, path=f"{APP_PATH}/../data-input/rki-reports/", lang=language
    )

    df_new.loc[:, "land"] = df_new.loc[:, "land"].apply(lambda x: x.replace("*", ""))

    # fmt: off
    # TODO: Refactor this part
    df_new = df_new[df_new.land != 'Federal State Total Number Number of Cases/ Number of'].drop_duplicates()

    df_new.loc[df_new['land'].str.contains('Schleswig-') == True, 'land'] = 'Schleswig-Holstein'
    df_new.loc[df_new['land'].str.contains('Baden-') == True, 'land'] = 'Baden-Wuerttemberg'
    df_new.loc[df_new['land'].str.contains('Bayern') == True, 'land'] = 'Bavaria'
    df_new.loc[df_new['land'].str.contains('Wuerttemberg') == True, 'land'] = 'Baden-Wuerttemberg'
    df_new.loc[df_new['land'].str.contains('Württemberg') == True, 'land'] = 'Baden-Wuerttemberg'
    df_new.loc[df_new['land'].str.contains('Saxony-') == True, 'land'] = 'Saxony-Anhalt'
    df_new.loc[df_new['land'].str.contains('Sachsen-') == True, 'land'] = 'Saxony-Anhalt'
    df_new.loc[df_new['land'] == 'Sachsen', 'land'] = 'Saxony'
    df_new.loc[df_new['land'].str.contains('Anhalt') == True, 'land'] = 'Saxony-Anhalt'
    df_new.loc[df_new['land'].str.contains('Mecklenburg-') == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df_new.loc[df_new['land'].str.contains('Western Pomerania') == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df_new.loc[df_new['land'].str.contains('Pomerania') == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df_new.loc[df_new['land'].str.contains('Vorpommern') == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df_new.loc[df_new['land'].str.contains('North') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Westphalia') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Westfalen') == True, 'land'] = 'North Rhine-Westphalia'
    # df_new.loc[df_new['land'].str.contains('Nordrhein-Westfalen') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Rhineland-') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Palatinate') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Pfalz') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Rheinland-') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Niedersachsen') == True, 'land'] = 'Lower Saxony'
    df_new.loc[df_new['land'].str.contains('Hessen') == True, 'land'] = 'Hesse'
    df_new.loc[df_new['land'].str.contains('Thüringen') == True, 'land'] = 'Thuringia'
    df_new.loc[df_new['land'].str.contains('Holstein') == True, 'land'] = 'Schleswig-Holstein'

    df_new.loc[df_new['land'].str.contains('Hamburg') == True, 'land'] = 'Hamburg'
    df_new.loc[df_new['land'].str.contains('Lower Saxony') == True, 'land'] = 'Lower Saxony'
    df_new.loc[df_new['land'].str.contains('Hesse') == True, 'land'] = 'Hesse'
    df_new.loc[df_new['land'].str.contains('Saarland') == True, 'land'] = 'Saarland'
    df_new.loc[(df_new['land'].str.contains('Saxony') == True)
               & (df_new['land'].str.contains('Lower') == False)
               & (df_new['land'].str.contains('-') == False), 'land'] = 'Saxony'
    df_new.loc[df_new['land'].str.contains('Thuringia') == True, 'land'] = 'Thuringia'
    df_new.loc[df_new['land'].str.contains('Bavaria') == True, 'land'] = 'Bavaria'
    df_new.loc[df_new['land'].str.contains('Berlin') == True, 'land'] = 'Berlin'
    df_new.loc[df_new['land'].str.contains('Brandenburg') == True, 'land'] = 'Brandenburg'
    df_new.loc[df_new['land'].str.contains('Bremen') == True, 'land'] = 'Bremen'
    # fmt: on
    # =========================================== PRINTING PARSING RESULT ======================================
    print("Printing Loaded Table")
    print(tabulate(df_new), "\n")
    print(
        tabulate(
            df_new.loc[:, ["land", "confirmed"]]
                .groupby(["land"])
                .count()
                .sort_values(["confirmed"], ascending=False)
        ),
        "\n",
    )

    # =========================================== SAVING PARSED RESULT ======================================
    df_new.to_csv(
        f"{APP_PATH}/../data-processed/tmp_rki_report.csv", index=False
    )
    # # =========================================== LOADING ACCUMULATED DATA TABLE =======================================
    # result_all = pd.read_csv(f"{APP_PATH}/../data-processed/rki-reports.csv")
    # result_all["date"] = result_all["date"].astype("datetime64[ns]")
    # df_new["date"] = df_new["date"].astype("datetime64[ns]")
    #
    # print("Printing Accumulated Table")
    # print(
    #     tabulate(
    #         result_all.loc[:, ["land", "confirmed"]]
    #             .groupby(["land"])
    #             .count()
    #             .sort_values(["confirmed"], ascending=False)
    #             .head(50)
    #     )
    # )
    #
    # # =========================================== JOINING NEW REPORT /W ACCUMULATED TABLE ==============================
    # result_concat = pd.concat([result_all, df_new]).sort_values("date", ascending=False)
    # # Drop Duplicates
    # result_concat = result_concat.drop_duplicates()
    # print("Printing Joined Table")
    # print(
    #     tabulate(
    #         result_concat.loc[:, ["land", "confirmed"]]
    #             .groupby(["land"])
    #             .count()
    #             .sort_values(["confirmed"], ascending=False)
    #             .head(50)
    #     )
    # )
    #
    # print("Please check the output above and proceed with saving if everything is fine")
    # print("To save type 'y' or 'yes'")
    # save_or_not = input()
    #
    # if save_or_not.lower() in ["y", "yes"]:
    #     print("Saving resulting DataFrame")
    #     result_concat.to_csv(
    #         f"{APP_PATH}/../data-processed/rki-reports.csv", index=False
    #     )
    # else:
    #     print("Aborted saving")
