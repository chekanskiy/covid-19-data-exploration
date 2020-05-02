import numpy as np
import pandas as pd


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
    df['dow'] = df.index.weekday
    df['weekend'] = df.index.weekday.isin([5,6])
    return df


def add_variables_covid(df, column='confirmed', population=False):
    df = add_weekday_weekend(df)

    df = add_lag(df, column, 1)  # df.loc[:,'confirmed_l1'] = df.loc[:,'confirmed'].shift(1)

    df.loc[:, f'{column}_avg3'] = np.round(df.loc[:, column].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, f'{column}_avg3_l1'] = df.loc[:, f'{column}_avg3'].shift(1)

    df[f'{column}_change'] = df[column] - df[f'{column}_l1']
    df.loc[:, f'{column}_change_avg3'] = np.round(df.loc[:, f'{column}_change'].rolling(3, win_type='triang').mean(), 0)

    df.loc[:, f'{column}_change_3w'] = np.round(df.loc[:, f'{column}_change'].rolling(21).sum(), 0)

    df = add_lag(df, f'{column}_change', 1)
    df = add_lag(df, f'{column}_change_avg3', 1)
    df = add_lag(df, f'{column}_change_3w', 1)

    df[f'{column}_change_pct'] = df[f'{column}_change'] / df[f'{column}_l1']
    df[f'{column}_change_pct_avg3'] = df[f'{column}_change_avg3'] / df[f'{column}_avg3_l1']
    df[f'{column}_change_pct_3w'] = df[f'{column}_change'] / df[f'{column}_change_3w_l1']

    df[f'{column}_change_acceleration'] = 1 - df[f'{column}_change'] / df[f'{column}_change_l1']
    df[f'{column}_change_acceleration_avg3'] = 1 - df[f'{column}_change_avg3'] / df[f'{column}_change_avg3_l1']

    df = add_doubling_time(df, f'{column}_change_pct', prefix=column)
    df = add_doubling_time(df, f'{column}_change_pct_3w', suffix='_3w', prefix=column)

    df.loc[:, f'{column}_doubling_days_avg3'] = np.round(df.loc[:, f'{column}_doubling_days'].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, f'{column}_doubling_days_3w_avg3'] = np.round(df.loc[:, f'{column}_doubling_days_3w'].rolling(3, win_type='triang').mean(), 0)

    if column == 'confirmed':
        df.loc[:, f'{column}_active_cases'] = df[f'{column}'] - df[f'{column}'].shift(12)
        df.loc[:, f'{column}_peak'] = np.log(df[f'{column}'] / df[f'{column}'].shift(12))

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
    df.loc[:, 'transit_avg3'] = np.round(
        df.loc[:, 'transit'].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, 'walking_avg3'] = np.round(
        df.loc[:, 'walking'].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, 'driving_avg3'] = np.round(
        df.loc[:, 'driving'].rolling(3, win_type='triang').mean(), 0)

    df = add_lag(df, 'transit', 1)
    df = add_lag(df, 'walking', 1)
    df = add_lag(df, 'driving', 1)

    df = add_lag(df, 'transit', 6)
    df = add_lag(df, 'walking', 6)
    df = add_lag(df, 'driving', 6)

    df['change_transit_l6'] = df['transit_l6'] - df['transit_l6'].shift(1)
    df['change_walking_l6'] = df['walking_l6'] - df['walking_l6'].shift(1)
    df['change_pct_driving_l6'] = df['driving_l6'] - df['driving_l6'].shift(1)
    
    df['change_transit'] = df['transit'] - df['transit'].shift(1)
    df['change_walking'] = df['walking'] - df['walking'].shift(1)
    df['change_driving'] = df['driving'] - df['driving'].shift(1)

    return df


def add_day_since(df, colunm, cutoff):
    df['day_since'] = 0
    df['day_since'] = df.apply(lambda x: x['day_since'] + 1 if x[colunm] > cutoff else 0, axis=1)
    df['day_since'] = df['day_since'].cumsum()
    return df


def join_series_day_since(dfs: dict, column):
    list_to_join = []
    for k in dfs.keys():
        df = dfs[k].loc[dfs[k].day_since > 0, [column] + ['day_since']]
        df.columns = [k] + ['day_since']
        df.set_index('day_since', inplace=True)
        list_to_join.append(df)

    return pd.concat(list_to_join, axis=1)

