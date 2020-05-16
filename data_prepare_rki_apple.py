import pandas as pd
import geopandas as gpd
import json
from features import add_variables_covid, add_variables_apple

date_apple = '2020-05-14'


def apple_filter_region(df, region):
    df_region = df[df.region == region].T
    df_region.columns = df_region.loc['transportation_type', :]
    df_region = df_region[~df_region.index.isin(['geo_type', 'region', 'transportation_type', 'alternative_name'])]

    df_region['dates'] = pd.to_datetime(df_region.index)
    df_region.set_index('dates', inplace=True)
    df_region = df_region.astype('float')
    df_region['region'] = region

    return df_region


def melt_apple_df(dfapple):
    _list = list()
    for region in dfapple.region.unique():
        dfapple_region = apple_filter_region(dfapple, region)
        df = add_variables_apple(dfapple_region)
        _list.append(df)
    ret = pd.concat([df for df in _list])
    return ret


def melt_rki_df(df_rki_germany):
    _list = list()
    for land in df_rki_germany.land.unique():
        df = df_rki_germany.loc[df_rki_germany.land == land, :].copy()
        pop = int(df.loc[df.land==land, 'population'][0])
        df = add_variables_covid(df, 'confirmed', population=pop)
        df = add_variables_covid(df, 'dead', population=pop)
        _list.append(df)
    return pd.concat([df for df in _list])


# ============================== LOAD DATA ==============================
df_rki_germany = pd.read_csv("data-RKI-parse/RKI-reports.csv")
df_population_de = pd.read_csv('german_lander_population.csv')
geojson_path = "../deutschlandGeoJSON/2_bundeslaender/3_mittel.geo.json"
dfapple = pd.read_csv(f"../AppleMobilty/applemobilitytrends-{date_apple}.csv")

# ============================== PREPARE LOADED DATA ==============================
df_rki_germany.drop('data', axis=1, inplace=True)

df_geojson = gpd.read_file(geojson_path)
df_geojson.columns = ["iso_code", 'name', 'type','geometry']
df_geojson = df_geojson.loc[:, ["iso_code", 'geometry']]
df_geojson['iso_code'] = df_geojson.iso_code.str.replace('DE-', '')
geojson = json.loads(df_geojson.set_index('iso_code').to_json())
json.dump(geojson, open('data_geo_de.json', 'w'))

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

# ============================== SAVE DATA ==============================
# RKI
df_rki_germany_processed.to_csv('data_rki_prepared.csv')
DASH_COLUMNS = ['land', 'date', 'iso_code', 'confirmed_change', 'confirmed', 'confirmed_active_cases', 'confirmed_change_per_100k',
                'confirmed_change_pct_3w', 'confirmed_doubling_days_3w_avg3', 'dead_change', 'dead', 'dead_change_per_100k', 'dead_doubling_days']
df_rki_germany_processed_dash = df_rki_germany_processed.loc[:, DASH_COLUMNS]
df_rki_germany_processed_dash.to_csv('data_rki_prepared_dash.csv')

# APPLE
df_apple_processed.to_csv('data_apple_prepared.csv')
df_apple_processed_de.to_csv('data_apple_prepared_de.csv')

# RKI & APPLE
df_rki_germany_processed_dash.index.name = None
df_rki_de_apple = df_apple_processed_de.merge(df_rki_germany_processed_dash, on=['date', 'land'], how='right')
for l in df_rki_de_apple.land.unique():
    df_rki_de_apple.loc[(df_rki_de_apple.land == l), ['driving', 'walking', 'transit']] = df_rki_de_apple.loc[ (df_rki_de_apple.land == l), ['driving', 'walking', 'transit']].fillna(method='ffill')
df_rki_de_apple.to_csv('data_rki_apple_prepared_dash.csv')
