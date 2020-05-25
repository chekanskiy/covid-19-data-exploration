import os
import pathlib
import sys
import warnings

import dotenv
import numpy as np
import pandas as pd
from features import add_variables_covid
from utils import DASH_COLUMNS, FEATURE_DROP_DOWN

DASH_COLUMNS = set(DASH_COLUMNS + list(FEATURE_DROP_DOWN.keys()))
pd.set_option('display.max_columns', 300)

warnings.filterwarnings("ignore")

dotenv.load_dotenv()
JHU_INPUT = os.environ.get("JHU_INPUT")
INPUT = os.environ.get("INPUT")
PROCESSED = os.environ.get("PROCESSED")
DASH_PROCESSED = os.environ.get("DASH_PROCESSED")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

path_jhu_data = f'{APP_PATH}{INPUT}'
path_input = f'{APP_PATH}{INPUT}'
path_processed = f'{APP_PATH}{PROCESSED}'
path_processed_dash = f'{APP_PATH}{DASH_PROCESSED}'
latest_apple_report = sorted(os.listdir(f'{APP_PATH}{INPUT}apple-mobility'), reverse=True)[0]
print(f'Loading {latest_apple_report} report')


def fix_countries(df):
    df.loc[df.state.str.contains('Hong Kong') == True, 'iso_code'] = 'HKG'
    df.loc[df.state.str.contains('Macau') == True, 'iso_code'] = 'MAC'
    df.loc[df.state.str.contains('Hong Kong') == True, 'state'] = np.NaN
    df.loc[df.state.str.contains('Macau') == True, 'state'] = np.NaN
    df.loc[df.iso_code.str.contains('HKG') == True, 'country'] = 'Hong Kong'
    df.loc[df.iso_code.str.contains('MAC') == True, 'country'] = 'Macau'

    s = df.loc[df.iso_code == 'CHN', [c for c in df.columns if '/20' in c]].sum()
    s['country'] = 'China'
    s['iso_code'] = 'CHN'
    df = pd.concat([df, s.to_frame().T, ], axis=0)

    s = df.loc[df.country.str.contains('Canada') == True, [c for c in df.columns if '/20' in c]].sum()
    s['country'] = 'Canada'
    s['iso_code'] = 'CAN'
    df = pd.concat([df, s.to_frame().T, ], axis=0)

    s = df.loc[df.country.str.contains('Australia') == True, [c for c in df.columns if '/20' in c]].sum()
    s['country'] = 'Australia'
    s['iso_code'] = 'AUS'
    df = pd.concat([df, s.to_frame().T, ], axis=0)

    return df


def prepare_df_country(df_confirmed, df_dead, df_population, country, date_cutoff=None):
    if date_cutoff is not None:
        df_confirmed = df_confirmed.loc[(df_confirmed.index >= date_cutoff) &
                                        (df_confirmed.country == country) &
                                        (df_confirmed['confirmed'] > 0), :]
        df_dead = df_dead.loc[(df_dead.index >= date_cutoff) &
                              (df_dead.country == country) &
                                        (df_dead['dead'] > 0), :]
    else:
        df_confirmed = df_confirmed.loc[(df_confirmed.country == country) &
                                        (df_confirmed['confirmed'] > 0), :]
        df_dead = df_dead.loc[(df_dead.country == country) &
                                        (df_dead['dead'] > 0), :]

    try:
        pop = df_population.loc[df_population.country == country, 'population'].values[0]
        iso_code = df_population.loc[df_population.country == country, 'iso_code'].values[0]
        region = df_population.loc[df_population.country == country, 'region'].values[0]
    except:
        print('No population data for :', country)
        return None

    df_confirmed = add_variables_covid(df_confirmed, 'confirmed', population=pop)

    df = df_confirmed.merge(df_dead, how='outer', on=['country', 'state', 'date'])

    df = add_variables_covid(df, column='dead', population=pop)

    # df['land'] = country
    df['iso_code'] = iso_code
    df['region_wb'] = region
    df['population_wb'] = pop

    return df


def country_iterate_jhu(df_confirmed, df_dead):
    _list = list()
    for country in df_confirmed.country.unique():
        df = prepare_df_country(df_confirmed, df_dead, df_population_joined, country)
        if df is not None:
            _list.append(df)
    return pd.concat([df for df in _list])


def melt_jhu_data(df, value_column):
    df = df.melt(id_vars=[c for c in df.columns if '/20' not in c],
                 value_vars=[c for c in df.columns if '/20' in c])
    df = df.rename({'variable': 'date', 'value': value_column}, axis=1)
    df['date'] = df['date'].astype('datetime64[ns]')
    if value_column != 'confirmed':
        # df = df.loc[['iso_code', 'lat', 'lng'], :]
        df.drop(['lat', 'lng', 'iso_code'], axis=1, inplace=True)
    df = df.sort_values(by=['country', 'state', 'date'], ascending=True)
    df = df.set_index('date', drop=False).rename_axis('date_index')
    # df[value_column] = df[value_column].astype(float)
    return df


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

    # Load EU country list
    df_eu_countries = pd.read_csv(f'{path_input}eu_countries.csv')

    # Load Apple Data
    # df_apple = pd.read_csv(f'{path_processed}/data_apple_prepared.csv')

    # Load WB Population Data
    df_population = pd.read_csv(f"{path_processed}wb/population.csv")

    # Pull the latest Data
    os.chdir(f'{APP_PATH}{JHU_INPUT}')
    os.system("git pull")
    os.chdir(f'{APP_PATH}')

    # Load JHU Data
    df_covid_conf = pd.read_csv(
        f"{APP_PATH}{JHU_INPUT}/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df_covid_dead = pd.read_csv(
        f"{APP_PATH}{JHU_INPUT}/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
    df_uid = pd.read_csv(f"{APP_PATH}{JHU_INPUT}/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv")

    df_uid = df_uid.loc[df_uid['Province_State'].isnull() == True, ['iso3', 'Country_Region']]
    df_uid.columns = ['iso_code', 'country']

    df_covid_conf.columns = ['state', 'country', 'lat', 'lng'] + list(df_covid_conf.columns[4:])
    df_covid_dead.columns = ['state', 'country', 'lat', 'lng'] + list(df_covid_dead.columns[4:])
    df_covid_conf = df_covid_conf.merge(df_uid, how='outer', on='country', suffixes=('_x', '_y'))
    df_covid_dead = df_covid_dead.merge(df_uid, how='outer', on='country', suffixes=('_x', '_y'))
    
    # Fix Country Names and Aggregate Countries by province
    df_covid_conf = fix_countries(df_covid_conf)
    df_covid_dead = fix_countries(df_covid_dead)

    # Take only aggregated countries
    df_covid_conf = df_covid_conf.loc[df_covid_conf['state'].isnull() == True, :]
    df_covid_dead = df_covid_dead.loc[df_covid_dead['state'].isnull() == True, :]

    # Join WB population
    df_population_joined = df_population.merge(df_covid_conf.loc[:, ['iso_code', 'country']].drop_duplicates(),
                                               how='outer', on='iso_code', suffixes=('_x', '_y'), left_index=False,
                                               right_index=False, )

    missing_popuation = df_population_joined.loc[df_population_joined.population.isnull() == True].sort_values(by='region')
    print(f"Missing population data for {len(missing_popuation)} countries\n")
    print(missing_popuation.country.unique(), '\n')

    missing_covid_data = df_population_joined.loc[df_population_joined.country_wb.isnull() == True].sort_values(
        by='region')
    print(f"Missing COVID data for {len(missing_covid_data)} countries\n")
    print(missing_covid_data.country.unique(), '\n')

    # Melt JHU Data into long format
    df_covid_conf_t = melt_jhu_data(df_covid_conf, 'confirmed')
    df_covid_dead_t = melt_jhu_data(df_covid_dead, 'dead')

    # Prepare variables
    df_jhu_processed = country_iterate_jhu(df_covid_conf_t, df_covid_dead_t).round(2)
    df_jhu_processed.rename({'country': 'land'}, axis=1, inplace=True)

    # Filter out countries where WB population data did not join
    df_jhu_processed = df_jhu_processed.loc[df_jhu_processed.region_wb.isnull() == False]

    # Join Apple Data
    # df_apple['date'] = df_apple['date'].astype('datetime64[ns]')
    # df_apple.rename({'country': 'land'}, axis=1, inplace=True)
    # df_jhu_processed['date'] = df_jhu_processed['date'].astype('datetime64[ns]')
    # df_jhu_processed = df_jhu_processed.merge(
    #     df_apple.loc[:, ['land', 'date', 'driving', 'walking', 'transit']], on=['date', 'land'], how='left')
    # print("merged", len(df_jhu_processed))
    # for land in df_jhu_processed.land.unique():
    #     df_jhu_processed.loc[(df_jhu_processed.land == land), ['driving', 'walking', 'transit']] = \
    #         df_jhu_processed.loc[(df_jhu_processed.land == land), ['driving', 'walking', 'transit']].fillna(method='ffill')

    # Add extra region "EU Countries"
    df_jhu_processed.loc[df_jhu_processed.land.isin(df_eu_countries.Country) == True, 'region_wb'] = 'European Union'

    df_jhu_processed.to_csv(f'{path_processed}data_jhu_world.csv', index=False)
    if subset_columns:
        df_jhu_processed.loc[:, [c for c in df_jhu_processed.columns if c in DASH_COLUMNS]].to_csv(f'{path_processed_dash}data_jhu_world.csv', index=False)
    else:
        df_jhu_processed.to_csv(f'{path_processed_dash}data_jhu_world.csv', index=False)
