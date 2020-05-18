from tabula import read_pdf
from tabulate import tabulate
import datetime
import pandas as pd
import pathlib
import sys

import warnings
warnings.simplefilter("ignore")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)


def extract_text(l):
    return "".join([k for k in l if not k.isdigit() and not k in [".", ",", "+"]]).rstrip()


def extract_numbers(l, el=None):
    result = [int(m) for m in "".join([k for k in l if k.isdigit() or k in [" "]]).lstrip().rstrip().split(" ") if len(m) > 0]
    if len(result) < 4:
        result += [0]*(4-len(result))
    if el is None:
        return result
    else:
        return result[el]


def count_numbers(l):
    c = 0
    try:
        c += sum([1 for k in l if k.isdigit()])
        return c
    except:
        return c


def extract_number(l):
    result = "".join([k for k in l.values[0] if k.isdigit()]).lstrip().rstrip()
    if len(result) > 0:
        return int(result)
    else:
        return 0


def fix_misaligned_row(df):
    df = df.reset_index(drop=True)
    for row in df.itertuples():
        try:
            if row.land != 'nan' and "Mecklenburg" not in row.land and pd.isnull(sum(row[2:])) == True:
                prev_index = row[0]-1
                df.loc[prev_index, 'land'] = (str(df.loc[prev_index, 'land']).replace('nan', '') + ' ' + str(row.land).replace('nan', '')).strip()
            if "Mecklenburg" in row.land or "Pomerania" in row.land:
                df.loc[df.land == row.land, 'land'] = 'Mecklenburg-Western Pomerania'
        except:
            pass
    return df


def load_pdf(date, path, lang="en"):
    path += '{0}-{1}.pdf'.format(date, lang)
    print(path)
    df = read_pdf(path, pages=[2])
    df = df[0].iloc[4:]
    try:
        print("Extracting single data column")
        df.columns = ['data']
        df['c'] = df.loc[:, 'data'].apply(count_numbers)
        df = fix_misaligned_row(df)
        df = df[df.c != 0]
        df['land'] = df.loc[:, 'data'].apply(extract_text)
        df['confirmed'] = df.loc[:, 'data'].apply(extract_numbers, args=[0])
        df['daily'] = df.loc[:, 'data'].apply(extract_numbers, args=[1])
        df['per_mil'] = df.loc[:, 'data'].apply(extract_numbers, args=[2])
        df['dead'] = df.loc[:, 'data'].apply(extract_numbers, args=[3])
    except:
        if len(df.columns) == 4:
            print("Extracting 4 data columns")
            df.columns = ['land', 'confirmed', 'daily', 'dead']
            df['per_mil'] = 0
            df = df.loc[:, ['land', 'confirmed', 'daily', 'per_mil', 'dead']]
        elif len(df.columns) == 5:
            print("Extracting 5 data columns")
            df.columns = ['land', 'confirmed', 'daily', 'per_mil', 'dead']
        elif len(df.columns) == 6:
            print("Extracting 6 data columns")
            df.columns = ['land', 'confirmed', 'daily', 'per_mil', 'dead', 'dead_per_100k']
            print(df.head(20))
        else:
            print(f"Falied to exctract {len(df.columns)} data columns")
            print(df)
            raise Exception
        df = fix_misaligned_row(df)
        df.drop(['dead_per_100k'], axis=1, inplace=True)
        df['c'] = df.loc[:, 'confirmed'].apply(count_numbers)
        df = df.loc[df.c != 0, :]
        df.loc[:,['confirmed']] = df.loc[:,['confirmed']].apply(extract_number, axis=1)
        df.loc[:,['daily']] = df.loc[:,['daily']].apply(extract_number, axis=1)
        df.loc[:,['dead']] = df.loc[:,['dead']].apply(extract_number, axis=1)
    df.loc[df.land.isnull() == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df = df.loc[(df.land.str.contains('cases') == False) & (df.land != 'Total')
                & (df.land.str.contains('Gesamt') == False), :]
    try:
        df['date'] = datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        df['date'] = date
    df.drop('c', axis=1, inplace=True)
    return df.reset_index(drop=True)


if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta

    date_yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--language", default="en", help="Report language: en for English, de for German"
    )
    parser.add_argument(
        "--date", default=date_yesterday, help="Report Date: YYYY-MM-DD",
    )

    args = parser.parse_args()
    date = args.date
    language = args.language

    # =========================================== LOADING AND PARSING REPORT ======================================
    df_new = load_pdf(date, path=f'{APP_PATH}/../data-input/rki-reports/', lang=language)
    df_new.drop(['daily', 'per_mil'], axis=1, inplace=True)

    df_new.loc[:, 'land'] = df_new.loc[:, 'land'].apply(lambda x: x.replace('*', ''))

    df_new = df_new[df_new.land != 'Federal State Total Number Number of Cases/ Number of'].drop_duplicates()

    df_new.loc[df_new['land'].str.contains('Schleswig-Holstein') == True, 'land'] = 'Schleswig-Holstein'
    df_new.loc[df_new['land'].str.contains('Baden-W') == True, 'land'] = 'Baden-Wuerttemberg'
    df_new.loc[df_new['land'].str.contains('Saxony-A') == True, 'land'] = 'Saxony-Anhalt'
    df_new.loc[df_new['land'].str.contains('Sachsen-Anhalt') == True, 'land'] = 'Saxony-Anhalt'
    df_new.loc[df_new['land'].str.contains('Mecklenburg-W') == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df_new.loc[df_new['land'].str.contains('Mecklenburg-V') == True, 'land'] = 'Mecklenburg-Western Pomerania'

    df_new.loc[df_new['land'].str.contains('Nordrhein-Westfalen') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Sachsen') == True, 'land'] = 'Saxony'
    df_new.loc[df_new['land'].str.contains('Rheinland-Pfalz') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Niedersachsen') == True, 'land'] = 'Lower Saxony'
    df_new.loc[df_new['land'].str.contains('Hessen') == True, 'land'] = 'Hesse'
    df_new.loc[df_new['land'].str.contains('Thüringen') == True, 'land'] = 'Thuringia'

    # =========================================== PRINTING PARSING RESULT ======================================
    print(tabulate(df_new), '\n')
    print(tabulate(df_new.loc[:, ['land', 'confirmed']].
                   groupby(['land']).count().sort_values(['confirmed'], ascending=False)), '\n')

    # =========================================== LOADING ACCUMULATED DATA TABLE =======================================
    result_all = pd.read_csv(f'{APP_PATH}/../data-processed/rki-reports.csv')
    result_all['date'] = result_all['date'].astype('datetime64[ns]')
    df_new['date'] = df_new['date'].astype('datetime64[ns]')

    print(tabulate(result_all.loc[:, ['land', 'confirmed']].
                   groupby(['land']).count().sort_values(['confirmed'], ascending=False).head(50)))

    # =========================================== JOINING NEW REPORT /W ACCUMULATED TABLE ==============================
    result_concat = pd.concat([result_all, df_new]).sort_values('date', ascending=False)
    # Drop Duplicates
    result_concat = result_concat.drop_duplicates()
    print(tabulate(result_concat.loc[:, ['land', 'confirmed']].
                   groupby(['land']).count().sort_values(['confirmed'], ascending=False).head(50)))

    print('Please check the output above and proceed with saving if everything is fine')
    print("To save type 'y' or 'yes'")
    save_or_not = input()

    if save_or_not.lower() in ['y', 'yes']:
        print('Saving resulting DataFrame')
        result_concat.to_csv(f'{APP_PATH}/../data-processed/rki-reports.csv', index=False)
    else:
        print('Aborted saving')
