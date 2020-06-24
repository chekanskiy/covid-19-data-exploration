from tabulate import tabulate
import pandas as pd
import pathlib
import sys

import warnings

warnings.simplefilter("ignore")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

# =========================================== SAVING PARSED RESULT ======================================
df_new = pd.read_csv(
    f"{APP_PATH}/../data-processed/tmp_rki_report.csv")
# =========================================== LOADING ACCUMULATED DATA TABLE =======================================
result_all = pd.read_csv(f"{APP_PATH}/../data-processed/rki-reports.csv")
result_all["date"] = result_all["date"].astype("datetime64[ns]")
df_new["date"] = df_new["date"].astype("datetime64[ns]")

print("Printing Accumulated Table")
print(
    tabulate(
        result_all.loc[:, ["land", "confirmed"]]
            .groupby(["land"])
            .count()
            .sort_values(["confirmed"], ascending=False)
            .head(50)
    )
)

# =========================================== JOINING NEW REPORT /W ACCUMULATED TABLE ==============================
result_concat = pd.concat([result_all, df_new]).sort_values("date", ascending=False)
# Drop Duplicates
result_concat = result_concat.drop_duplicates()
print("Printing Joined Table")
print(
    tabulate(
        result_concat.loc[:, ["land", "confirmed"]]
            .groupby(["land"])
            .count()
            .sort_values(["confirmed"], ascending=False)
            .head(50)
    )
)

# print("Please check the output above and proceed with saving if everything is fine")
# print("To save type 'y' or 'yes'")
# save_or_not = input()
# if save_or_not.lower() in ["y", "yes"]:
#     print("Saving resulting DataFrame")
#     result_concat.to_csv(
#         f"{APP_PATH}/../data-processed/rki-reports.csv", index=False
#     )
# else:
#     print("Aborted saving")

result_concat.to_csv(
        f"{APP_PATH}/../data-processed/rki-reports.csv", index=False
    )