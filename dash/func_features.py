import pandas as pd


def join_series_day_since(df, column, day_since_column):
    df = df.loc[:, ['land', column, day_since_column]]
    df.loc[:, day_since_column] = df.loc[:, day_since_column].astype(int)
    df.loc[:, column] = df.loc[:, column].astype(float)

    max_days = max(df.loc[:, day_since_column])
    df_index = pd.DataFrame(index=list(range(1, max_days + 1)))
    for k in df.land.unique():
        df1 = df.loc[(df['land'] == k) & (df[day_since_column] > 0), [column, day_since_column]]
        df1.columns = [k, day_since_column]
        df1.set_index(day_since_column, inplace=True)
        df_index = df_index.join(df1, how='outer')

    return df_index.drop_duplicates()
