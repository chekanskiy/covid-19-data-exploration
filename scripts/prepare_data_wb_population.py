import pandas as pd
import dotenv
import os, sys
import pathlib
import world_bank_data as wb

dotenv.load_dotenv()
INPUT = os.environ.get("INPUT")
PROCESSED = os.environ.get("PROCESSED")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

path_input = f"{APP_PATH}{INPUT}"
path_processed = f"{APP_PATH}{PROCESSED}"

# Getting report from WB
countries = wb.get_countries()
# population = wb.get_series('SP.POP.TOTL', mrv=1)  # Most recent value
population = wb.get_series("SP.POP.TOTL", id_or_value="id", simplify_index=True, mrv=1)

# Saving Raw Reports
countries.to_csv(f"{path_input}wb/countries.csv")
population.to_csv(f"{path_input}wb/population.csv")

# Aggregate region, country and population
df_population = (
    countries[["region", "name"]]
    .rename(columns={"name": "country_wb"})
    .loc[countries.region != "Aggregates"]
)
df_population["population"] = population
df_population["country_wb"] = df_population["country_wb"].astype("string")
df_population["iso_code"] = df_population.index

# Fix Kosovo
df_population.loc[df_population.iso_code == "XKX", "iso_code"] = "XKS"

df_population.to_csv(f"{path_processed}wb/population.csv")
