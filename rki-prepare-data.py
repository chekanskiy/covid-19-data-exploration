import pandas as pd
import geopandas as gpd
import json
from features import add_variables_covid


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
df_rki_germany.set_index('date', inplace=True)

# ============================== PROCESS RKI REPORT FOR EACH COUNTRY ==============================
df_rki_germany_processed = melt_rki_df(df_rki_germany)
print("RKI max date", max(df_rki_germany_processed.index))

# ============================== SAVE DATA ==============================
df_rki_germany_processed.to_csv('data_rki_prepared.csv')

