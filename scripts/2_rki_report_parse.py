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
    if date <= '2020-03-04':
        return f"{APP_PATH}/templates/2020-03-04-en.tabula-template.json"
    elif date <= '2020-03-07':
        return f"{APP_PATH}/templates/2020-03-06-en.tabula-template.json"
    elif date <= '2020-03-08':
        return f"{APP_PATH}/templates/2020-03-08-en.tabula-template.json"
    elif date <= '2020-03-09':
        return f"{APP_PATH}/templates/2020-03-09-en.tabula-template.json"
    elif date <= '2020-03-10':
        return f"{APP_PATH}/templates/2020-03-10-en.tabula-template.json"
    elif date <= '2020-03-11':
        return f"{APP_PATH}/templates/2020-03-11-en.tabula-template.json"
    elif date <= '2020-03-14':
        return f"{APP_PATH}/templates/2020-03-12-en.tabula-template.json"
    elif date <= '2020-03-16':
        return f"{APP_PATH}/templates/2020-03-15-en.tabula-template.json"
    elif date <= '2020-03-18':
        return f"{APP_PATH}/templates/2020-03-17-en.tabula-template.json"
    elif date <= '2020-03-19':
        return f"{APP_PATH}/templates/2020-03-19-en.tabula-template.json"
    elif date <= '2020-03-21':
        return f"{APP_PATH}/templates/2020-03-20-en.tabula-template.json"
    elif date <= '2020-03-22':
        return f"{APP_PATH}/templates/2020-03-22-en.tabula-template.json"
    elif date <= '2020-03-23':
        return f"{APP_PATH}/templates/2020-03-23-en.tabula-template.json"
    elif date <= '2020-03-24':
        return f"{APP_PATH}/templates/2020-03-24-en.tabula-template.json"
    elif date <= '2020-05-19':
        return f"{APP_PATH}/templates/2020-05-18-en.tabula-template.json"
    elif date <= '2020-05-21':
        return f"{APP_PATH}/templates/2020-05-20-en.tabula-template.json"
    elif date <= '2020-05-22':
        return f"{APP_PATH}/templates/2020-05-22-en.tabula-template.json"
    elif date <= '2020-05-23':
        return f"{APP_PATH}/templates/2020-05-23-en.tabula-template.json"
    elif date <= '2020-05-24':
        return f"{APP_PATH}/templates/2020-05-24-en.tabula-template.json"
    else:
        return f"{APP_PATH}/templates/2020-05-25-en.tabula-template.json"


def extract_text(l):
    return "".join([k for k in l if not k.isdigit() and not k in [".", ",", "+"]]).rstrip()


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
        if '.' in str(result):
            if len(str(result).split('.')[1]) > 2:
                # print(result)
                result = int(fix_string(str(result)).replace('.', ''))
                return result
        elif ',' in str(result):
            if len(str(result).split(',')[1]) > 2:
                # print(result)
                result = int(fix_string(str(result)).replace(',', ''))
                return result
        return int(fix_string(str(result)))


def fix_misaligned_row(df):
    land_first_names = ["Mecklenburg-", 'Baden-', 'North Rhine-', 'Rhineland-',
                        'Saxony-', 'Schleswig-', 'Lower', 'Sachsen-']
    land_single_word_names = ["Bavaria", 'Berlin', 'Brandenburg', 'Bremen',
                              'Hamburg', 'Saarland', 'Thuringia', 'Hesse']
    df = df.reset_index(drop=True)
    for row in df.itertuples():
        try:
            # if land is not empty and values are null and land is not the beginning of other names
            if row.land != 'nan' and \
                    row.land.strip() not in land_first_names and \
                    pd.isnull(sum(row[2:])) == True:
                prev_index = row[0] - 1
                if df.loc[prev_index, 'land'] not in land_single_word_names:
                    df.loc[prev_index, 'land'] = (
                                str(df.loc[prev_index, 'land']).replace('nan', '') +
                                ' ' + str(row.land).replace('nan', '')).strip()
        except:
            pass
    return df


def load_pdf(date, path, lang="en"):
    path += '{0}-{1}.pdf'.format(date, lang)
    if date <= '2020-05-27':
        template = select_template(date, APP_PATH)
        print(path, '\n', template)
        dfs = read_pdf_with_template(path, pandas_options={'header': None, 'dtype': str}, template_path=template)
    else:
        if date <= '2020-05-28':
            area = [304, 69, 674, 547]  # Points: Top Y, Left X, Bottom Y, Right X
            columns = [160, 205, 254, 319, 370, 432, 476]  # Points: X coordinates of column splits
        else:
            area = [304, 69, 674, 547]   # Points: Top Y, Left X, Bottom Y, Right X
            columns = [160, 205, 254, 319, 370, 432, 476]  # Points: X coordinates of column splits
        dfs = read_pdf(path, pandas_options={'header': None, 'dtype': str}, stream=True, pages=2, area=area, columns=columns)

    print(dfs, '\n' * 2)
    df = dfs[0]
    if len(df.columns) == 2:
        print("Extracting 2 data columns")
        df.columns = ['land', 'confirmed']
        df = df.loc[:, ['land', 'confirmed']]
    elif len(df.columns) == 4:
        if date > '2020-03-24':
            print("Extracting 4 data columns after '2020-03-24'")
            df.columns = ['land', 'confirmed', 'daily', 'dead']
            df['per_mil'] = 0
            df = df.loc[:, ['land', 'confirmed', 'daily', 'per_mil', 'dead']]
        else:
            print("Extracting 4 data columns before '2020-03-24'")
            df.columns = ['land', 'confirmed', 'electronically_submitted', 'per_100k']
            df['per_mil'] = 0
            df = df.loc[:, ['land', 'confirmed']]
    elif len(df.columns) == 5:
        print("Extracting 5 data columns")
        df.columns = ['land', 'confirmed', 'daily', 'per_mil', 'dead']
    elif len(df.columns) == 6:
        print("Extracting 6 data columns")
        df.columns = ['land', 'confirmed', 'daily', 'per_mil', 'dead', 'dead_per_100k']
    elif len(df.columns) == 8:
        print("Extracting 6 data columns")
        df.columns = ['land', 'confirmed', 'daily', 'per_mil', '7day_sum', '7day_100k', 'dead', 'dead_per_100k']
    else:
        print(f"Falied to exctract {len(df.columns)} data columns")
        print(df.head(20))
        raise Exception
    df = fix_misaligned_row(df)
    df['c'] = df.loc[:, 'confirmed'].apply(count_numbers)
    df = df.loc[df.c != 0, :]
    df.loc[:, ['confirmed']] = df.loc[:, ['confirmed']].apply(extract_number, axis=1)
    if 'dead' in df.columns:
        df.loc[:, ['dead']] = df.loc[:, ['dead']].apply(extract_number, axis=1)
    else:
        df['dead'] = 0
    df.loc[df.land.isnull() == True, 'land'] = 'Mecklenburg-Western Pomerania'
    df = df.loc[(df.land.str.contains('cases') == False) & (df.land != 'Total')
                & (df.land.str.contains('Gesamt') == False), :]
    try:
        df['date'] = datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        df['date'] = date
    df = df.loc[:, ['land', 'confirmed', 'dead', 'date']]
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

    df_new.loc[:, 'land'] = df_new.loc[:, 'land'].apply(lambda x: x.replace('*', ''))

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
    df_new.loc[df_new['land'].str.contains('Westphalia') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Rhineland-') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Palatinate') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Pfalz') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Nordrhein-Westfalen') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Westfalen') == True, 'land'] = 'North Rhine-Westphalia'
    df_new.loc[df_new['land'].str.contains('Rheinland-') == True, 'land'] = 'Rhineland-Palatinate'
    df_new.loc[df_new['land'].str.contains('Niedersachsen') == True, 'land'] = 'Lower Saxony'
    df_new.loc[df_new['land'].str.contains('Hessen') == True, 'land'] = 'Hesse'
    df_new.loc[df_new['land'].str.contains('Thüringen') == True, 'land'] = 'Thuringia'
    df_new.loc[df_new['land'].str.contains('Holstein') == True, 'land'] = 'Schleswig-Holstein'

    # =========================================== PRINTING PARSING RESULT ======================================
    print('Printing Loaded Table')
    print(tabulate(df_new), '\n')
    print(tabulate(df_new.loc[:, ['land', 'confirmed']].
                   groupby(['land']).count().sort_values(['confirmed'], ascending=False)), '\n')

    # =========================================== LOADING ACCUMULATED DATA TABLE =======================================
    result_all = pd.read_csv(f'{APP_PATH}/../data-processed/rki-reports.csv')
    result_all['date'] = result_all['date'].astype('datetime64[ns]')
    df_new['date'] = df_new['date'].astype('datetime64[ns]')

    print('Printing Accumulated Table')
    print(tabulate(result_all.loc[:, ['land', 'confirmed']].
                   groupby(['land']).count().sort_values(['confirmed'], ascending=False).head(50)))

    # =========================================== JOINING NEW REPORT /W ACCUMULATED TABLE ==============================
    result_concat = pd.concat([result_all, df_new]).sort_values('date', ascending=False)
    # Drop Duplicates
    result_concat = result_concat.drop_duplicates()
    print('Printing Joined Table')
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
