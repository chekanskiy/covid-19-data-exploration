import numpy as np
import pandas as pd


def doubling_time(r):
    return round(np.log(2) / np.log(1+r),4)


def add_doubling_time(df, r_col, suffix=''):
    df['doubling_days' + suffix] = df[r_col].apply(doubling_time).apply(lambda x: x if x > 0 else 0).apply(lambda x: x if x < 100 else 100)
    return df


def add_lag(df, var, lag=1):
    new_var = var + f"_l{lag}"
    df.loc[:,new_var] = df.loc[:, var].shift(lag)
    return df


def add_weekday_weekend(df):
    df['dow'] = df.index.weekday
    df['weekend'] = df.index.weekday.isin([5,6])
    return df


def add_variables_covid(df, column='confirmed'):
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

    df = add_doubling_time(df, 'confirmed_change_pct')
    df = add_doubling_time(df, 'confirmed_change_pct_3w', suffix='_3w')

    df.loc[:, f'doubling_days_avg3'] = np.round(df.loc[:, f'doubling_days'].rolling(3, win_type='triang').mean(), 0)
    df.loc[:, f'doubling_days_3w_avg3'] = np.round(df.loc[:, f'doubling_days_3w'].rolling(3, win_type='triang').mean(),
                                                   0)

    # cleanup temp cols
    df.drop([f'{column}_l1',
             f'{column}_avg3_l1',
             f'{column}_change_l1',
             f'{column}_change_3w_l1',
             f'{column}_change_avg3_l1',
             #              '', '', '', '', '', ''
             ], axis=1, inplace=True)

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

    df['change_%_transit_l6'] = df['transit_l6'] / df['transit_l6'].shift(1)
    df['change_%_walking_l6'] = df['walking_l6'] / df['walking_l6'].shift(1)
    df['change_%_driving_l6'] = df['driving_l6'] / df['driving_l6'].shift(1)
