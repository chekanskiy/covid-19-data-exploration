import pandas as pd
import geopandas as gpd
import json
import pathlib
import os, sys
import dotenv
from features import add_variables_covid, add_variables_apple
from utils import DASH_COLUMNS

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
    apple_melted = dfapple.melt(id_vars=[c for c in dfapple.columns if '2020-' not in c], value_vars=[c for c in dfapple.columns if '2020-' in c])
    apple_melted.rename({'variable': 'date'}, axis=1, inplace=True)
    apple_melted.loc[:, [c for c in apple_melted.columns if c != 'value']] = apple_melted.loc[:, [c for c in apple_melted.columns if c != 'value']].fillna('n/a')
    apple_melted_pivoted = apple_melted.pivot_table(index=[c for c in apple_melted.columns if c not in ['value', 'transportation_type']],columns='transportation_type', values='value')
    apple_melted_pivoted = apple_melted_pivoted.reset_index()
    apple_melted_pivoted['date'] = apple_melted_pivoted['date'].astype('datetime64[ns]')
    apple_melted_pivoted = apple_melted_pivoted.set_index('date', drop=False).rename_axis('date_index', axis=0)
    return apple_melted_pivoted


def melt_rki_df(df_rki_germany):
    _list = list()
    for land in df_rki_germany.land.unique():
        df = df_rki_germany.loc[df_rki_germany.land == land, :].copy()
        pop = int(df.loc[df.land == land, 'population'][0])
        df = add_variables_covid(df, 'confirmed', population=pop)
        df = add_variables_covid(df, 'dead', population=pop)
        _list.append(df)
    return pd.concat([df for df in _list])


if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta

    date_yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--subset_columns", default=False, help="Take only a subset of columns for Dash Dashboard"
    )

    args = parser.parse_args()
    subset_columns = args.subset_columns
    if str(subset_columns).lower() in ['false', '0', 'no']:
        subset_columns = False

    # ============================== LOAD DATA ===================================================
    df_rki_germany = pd.read_csv(f"{path_processed}rki-reports.csv")
    df_population_de = pd.read_csv(f"{path_input}german_lander_population.csv")
    geojson_path = f"{path_input}deutschlandGeoJSON/2_bundeslaender/3_mittel.geo.json"
    dfapple = pd.read_csv(f"{path_input}apple-mobility/{latest_apple_report}")

    # ============================== LOAD AND SAVE SHAPE FILES ===================================

    df_geojson = gpd.read_file(geojson_path)
    df_geojson.columns = ["iso_code", 'name', 'type','geometry']
    df_geojson = df_geojson.loc[:, ["iso_code", 'geometry']]
    df_geojson['iso_code'] = df_geojson.iso_code.str.replace('DE-', '')
    geojson = json.loads(df_geojson.set_index('iso_code').to_json())
    json.dump(geojson, open(f'{path_processed}data_geo_de.json', 'w'))

    # ============================== JOIN RKI REPORT AND POPULATION ==============================

    df_rki_germany = df_rki_germany.merge(df_population_de,
                                            how='inner',
                                            left_on='land',
                                            right_on='name',
                                            left_index=False,
                                            right_index=False,
                                            suffixes=('_x', '_y'),)

    df_rki_germany['date'] = df_rki_germany['date'].astype('datetime64[ns]')
    df_rki_germany = df_rki_germany.sort_values('date', ascending=True)
    df_rki_germany.set_index('date', inplace=True, drop=False)

    # ============================== PROCESS RKI REPORT FOR EACH COUNTRY ==============================
    df_rki_germany_processed = melt_rki_df(df_rki_germany)
    print("RKI max date", max(df_rki_germany_processed.index))

    # ============================== PROCESS APPLE DATA FOR EACH REGION ==============================
    df_apple_processed = melt_apple_df(dfapple)
    apple_lands = {'Baden-Württemberg': 'Baden-Wuerttemberg',
                   'The Free Hanseatic City of Bremen':'Bremen',
                   'Mecklenburg-Vorpommern': 'Mecklenburg-Western Pomerania'
                  }
    df_apple_processed['region'] = df_apple_processed['region'].apply(lambda x: apple_lands.get(x) if apple_lands.get(x) is not None else x)

    df_apple_processed_de = df_apple_processed.loc[df_apple_processed.region.isin(df_rki_germany_processed.land.unique()), ['region', 'driving', 'walking', 'transit']]
    df_apple_processed_de['date'] = df_apple_processed_de.index
    df_apple_processed_de = df_apple_processed_de.rename(columns={'region': 'land'})

    # ============================== SAVE DATA ALL COLUMNS ==============================
    # RKI
    df_rki_germany_processed.rename_axis('date_index', axis=0, inplace=True)
    df_rki_germany_processed.sort_values(by=['land', 'date']).to_csv(f'{path_processed}/data_rki_prepared.csv')

    # APPLE
    df_apple_processed.rename_axis('date_index', axis=0, inplace=True)
    df_apple_processed.sort_values(by=['region', 'country', 'sub-region', 'date']).to_csv(f'{path_processed}/data_apple_prepared.csv')
    df_apple_processed_de.sort_values(by=['land', 'date']).to_csv(f'{path_processed}/data_apple_prepared_de.csv')

    # ============================== SAVE DATA DASH SUBSET ==============================
    # df_rki_germany_processed_dash.to_csv(f'{APP_PATH}/../dash/data/data_rki_prepared_dash.csv')

    # RKI & APPLE
    if subset_columns:
        print("Taking a subset of all columns for Dash")
        df_rki_germany_processed_dash = df_rki_germany_processed.loc[:, DASH_COLUMNS]
    else:
        print("Taking all columns for Dash")
        df_rki_germany_processed_dash = df_rki_germany_processed

    df_rki_germany_processed_dash.rename_axis('date_index', axis=0, inplace=True)

    df_rki_de_apple = df_apple_processed_de.merge(df_rki_germany_processed_dash, on=['date', 'land'], how='right')
    for l in df_rki_de_apple.land.unique():
        df_rki_de_apple.loc[(df_rki_de_apple.land == l), ['driving', 'walking', 'transit']] = df_rki_de_apple.loc[ (df_rki_de_apple.land == l), ['driving', 'walking', 'transit']].fillna(method='ffill')
    df_rki_de_apple.sort_values(by=['land', 'date']).to_csv(f'{APP_PATH}/../dash/data/data_rki_apple_prepared_dash.csv')
