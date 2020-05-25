import pandas as pd
import pathlib
import os, sys
import dotenv
from features import add_variables_apple
from utils import DASH_COLUMNS, FEATURE_DROP_DOWN

DASH_COLUMNS = set(DASH_COLUMNS + list(FEATURE_DROP_DOWN.keys()))

dotenv.load_dotenv()
INPUT = os.environ.get("INPUT")
PROCESSED = os.environ.get("PROCESSED")
DASH_PROCESSED = os.environ.get("DASH_PROCESSED")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

path_input = f'{APP_PATH}{INPUT}'
path_processed = f'{APP_PATH}{PROCESSED}'
save_path_dash = f'{APP_PATH}P{DASH_PROCESSED}'
latest_apple_report = sorted(os.listdir(f'{APP_PATH}{INPUT}apple-mobility'), reverse=True)[0]
print(f'Loading {latest_apple_report} report')


def melt_apple_df(dfapple):
    apple_melted = dfapple.melt(id_vars=[c for c in dfapple.columns if '2020-' not in c],
                                value_vars=[c for c in dfapple.columns if '2020-' in c])
    apple_melted.rename({'variable': 'date'}, axis=1, inplace=True)
    apple_melted.loc[:, [c for c in apple_melted.columns if c != 'value']] = apple_melted.loc[:,
                                                                             [c for c in apple_melted.columns if
                                                                              c != 'value']].fillna('n/a')
    apple_melted_pivoted = apple_melted.pivot_table(
        index=[c for c in apple_melted.columns if c not in ['value', 'transportation_type']],
        columns='transportation_type', values='value')
    apple_melted_pivoted = apple_melted_pivoted.reset_index()
    apple_melted_pivoted['date'] = apple_melted_pivoted['date'].astype('datetime64[ns]')
    apple_melted_pivoted = apple_melted_pivoted.set_index('date', drop=False).rename_axis('date_index', axis=0)
    return apple_melted_pivoted


if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta

    date_yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--subset_columns", default=True, help="Take only a subset of columns for Dash Dashboard"
    )

    args = parser.parse_args()
    subset_columns = args.subset_columns
    if str(subset_columns).lower() in ['false', '0', 'no']:
        subset_columns = False

    # ============================== LOAD DATA ===================================================
    dfapple = pd.read_csv(f"{path_input}apple-mobility/{latest_apple_report}")

    # ============================== PROCESS APPLE DATA FOR EACH REGION ==============================
    df_apple_processed = melt_apple_df(dfapple)
    apple_lands_rename = {'Baden-Württemberg': 'Baden-Wuerttemberg',
                          'The Free Hanseatic City of Bremen': 'Bremen',
                          'Mecklenburg-Vorpommern': 'Mecklenburg-Western Pomerania'
                          }
    apple_countries_rename = {'United States': 'US', 'Republic of Korea': 'Korea, South',
                              'Czech Republic': 'Czechia', 'Taiwan': 'Taiwan*'}
    df_apple_processed['region'] = df_apple_processed['region'].apply(
        lambda x: apple_lands_rename.get(x) if apple_lands_rename.get(x) is not None else x)
    df_apple_processed['country'] = df_apple_processed['country'].replace()

    df_apple_processed['date'] = df_apple_processed.index

    # ============================== SAVE DATA ALL COLUMNS ==============================
    # APPLE
    df_apple_processed.rename_axis('date_index', axis=0, inplace=True)
    df_apple_processed.sort_values(by=['region', 'country', 'sub-region', 'date']).to_csv(
        f'{path_processed}/data_apple_prepared.csv')
