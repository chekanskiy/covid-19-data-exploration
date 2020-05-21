import numpy as np
import pandas as pd
import datetime


def doubling_time(r):
    return round(np.log(2) / np.log(1+r),4)


def add_doubling_time(df, r_col, prefix, suffix=''):
    df[prefix + '_doubling_days' + suffix] = df[r_col].apply(doubling_time).apply(lambda x: x if x > 0 else 0).apply(lambda x: x if x < 100 else 100)
    return df


def add_lag(df, var, lag=1):
    new_var = var + f"_l{lag}"
    df.loc[:,new_var] = df.loc[:, var].shift(lag)
    return df


def add_weekday_weekend(df):
    df['dow'] = 0
    df['weekend'] = 0
    df.loc[:, 'dow'] = df.index.weekday
    df.loc[:, 'weekend'] = df.index.weekday.isin([5, 6])
    return df


def add_day_since(df, colunm, cutoff):
    df[f'{colunm}_day_since_{cutoff}'] = 0
    df[f'{colunm}_day_since_{cutoff}'] = df.apply(lambda x: x[f'{colunm}_day_since_{cutoff}'] + 1 if x[colunm] > cutoff else 0, axis=1)
    df[f'{colunm}_day_since_{cutoff}'] = df[f'{colunm}_day_since_{cutoff}'].cumsum()
    return df


def add_variables_covid(df, column='confirmed', population=False):

    # df.loc[df[column] == 0, column] = np.NaN
    df.loc[df[column] < 0, column] = 0

    df = add_lag(df, column, 1)  # df.loc[:,'confirmed_l1'] = df.loc[:,'confirmed'].shift(1)

    df.loc[:, f'{column}_avg3'] = np.round(df.loc[:, column].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, f'{column}_avg3_l1'] = df.loc[:, f'{column}_avg3'].shift(1)

    df[f'{column}_change'] = df[column] - df[f'{column}_l1']
    df.loc[:, f'{column}_change_avg3'] = np.round(df.loc[:, f'{column}_change'].rolling(3, win_type='triang').mean(), 0)

    df.loc[:, f'{column}_change_3w'] = np.round(df.loc[:, f'{column}_change'].rolling(21).sum(), 0)

    df = add_lag(df, f'{column}_change', 1)
    df = add_lag(df, f'{column}_change_avg3', 1)
    df = add_lag(df, f'{column}_change_3w', 1)

    df[f'{column}_change_pct'] = df[f'{column}_change'] / df[f'{column}_l1'].replace({0: np.NaN})
    df[f'{column}_change_pct_avg3'] = df[f'{column}_change_avg3'].divide(df[f'{column}_avg3_l1'].replace({0: np.NaN}))
    df[f'{column}_change_pct_3w'] = df[f'{column}_change'].divide(df[f'{column}_change_3w_l1'].replace({0: np.NaN}))

    df = add_doubling_time(df, f'{column}_change_pct', prefix=column)
    df = add_doubling_time(df, f'{column}_change_pct_3w', suffix='_3w', prefix=column)

    df.loc[:, f'{column}_doubling_days_avg3'] = np.round(df.loc[:, f'{column}_doubling_days'].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, f'{column}_doubling_days_3w_avg3'] = np.round(df.loc[:, f'{column}_doubling_days_3w'].rolling(3, win_type='triang').mean(), 0)

    if column == 'confirmed':
        df.loc[:, f'{column}_active_cases'] = df[f'{column}'] - df[f'{column}'].shift(12)
        df.loc[:, f'{column}_peak'] = np.log((df[f'{column}'] / df[f'{column}'].shift(12)).replace({0: np.NaN}))
        
    df = add_day_since(df, column, 10)

    # cleanup temp cols
    df.drop([f'{column}_l1',
             f'{column}_avg3_l1',
             f'{column}_change_l1',
             f'{column}_change_3w_l1',
             f'{column}_change_avg3_l1',
             #              '', '', '', '', '', ''
             ], axis=1, inplace=True)

    if population:
        df[f'{column}_per_100k'] = df[f'{column}'] / round(population / 100000, 3)
        df[f'{column}_change_per_100k'] = df[f'{column}_change'] / round(population / 100000, 3)

    df = df.round(3)

    return df


def add_variables_apple(df):
    if 'transit' in df.columns:
        df.loc[:, 'transit_avg3'] = np.round(
            df.loc[:, 'transit'].rolling(3, win_type='triang').mean(), 0)
        df = add_lag(df, 'transit', 1)
        df = add_lag(df, 'transit', 6)
        df['change_transit_l6'] = df['transit_l6'] - df['transit_l6'].shift(1)
        df['change_transit'] = df['transit'] - df['transit'].shift(1)
        
    if 'walking' in df.columns:
        df.loc[:, 'walking_avg3'] = np.round(
            df.loc[:, 'walking'].rolling(3, win_type='triang').mean(), 0)
        df = add_lag(df, 'walking', 1)
        df = add_lag(df, 'walking', 6)
        df['change_walking_l6'] = df['walking_l6'] - df['walking_l6'].shift(1)
        df['change_walking'] = df['walking'] - df['walking'].shift(1)
        
    if 'driving' in df.columns:
        df.loc[:, 'driving_avg3'] = np.round(
            df.loc[:, 'driving'].rolling(3, win_type='triang').mean(), 0)
        df = add_lag(df, 'driving', 1)
        df = add_lag(df, 'driving', 6)
        df['change_pct_driving_l6'] = df['driving_l6'] - df['driving_l6'].shift(1)
        df['change_driving'] = df['driving'] - df['driving'].shift(1)

    return df


def join_series_day_since(dfs: dict, column, day_since_column):
    max_days = 0
    for k in dfs.keys():
        max_days_since = max(dfs[k].loc[:, day_since_column])
        if max_days < max_days_since:
            max_days = max_days_since
    df_index = pd.DataFrame(index=list(range(1, max_days + 1)))
    list_to_join = [df_index]
    for k in dfs.keys():
        df = dfs[k].loc[dfs[k][day_since_column] > 0, [column, day_since_column]]
        df.columns = [k, day_since_column]
        df.set_index(day_since_column, inplace=True)
        df_index = df_index.join(df, how='outer')

    return df_index.drop_duplicates()


def join_series_date(dfs: dict, column):
    max_days = datetime.date(2020, 1, 1)
    min_days = datetime.date(2020, 3, 15)
    for k in dfs.keys():
        max_days_since = max(dfs[k].index)
        min_days_since = min(dfs[k].index)
        if max_days < max_days_since:
            max_days = max_days_since
        if min_days > min_days_since:
            min_days = min_days_since
    df_index = pd.DataFrame(index=list(pd.date_range(min_days, max_days)))
    list_to_join = [df_index]
    for k in dfs.keys():
        df = dfs[k].loc[:,[column]]
        df.columns = [k]
#         df.set_index('day_since', inplace=True)
        df_index = df_index.join(df, how='outer')

    return df_index.drop_duplicates()
