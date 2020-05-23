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
    df.loc[:, new_var] = df.loc[:, var].shift(lag)
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


def peak_end_trend(df):
    df_peak_log = df.loc[:, ['confirmed_peak_log']].dropna()

    from sklearn.linear_model import LinearRegression
    days_pred_start = 10  # for how long to draw  the trend
    days_since_first_peak_start = 7  # how many days to wait since the first outbreak before estimating trend
    days_other_peak_starts = 7  # how many days since the second+ outbreak should pass before calculating trend

    # is we do not have enough data then exit
    if len(df.loc[:, ['confirmed_peak_log']].dropna()) < days_since_first_peak_start:
        df['peak_log_trend'] = np.NaN
        return df
    # find all indixes of outbreak beginnings
    peak_indixes = df.loc[df.confirmed_peak_date == 1].index.tolist()
    #     peak_indixes[0] = df_peak_log.index.min()

    # iterate over peak indixes
    for i, index in enumerate(peak_indixes):
        peak_index = peak_indixes[i]
        days_pred = days_pred_start
        if i == 0:
            # select y values since the beginning of the outbreak till defined number of days
            # and take a 3 days moving average for a smother trend
            days_add = days_since_first_peak_start
            if len(peak_indixes) > 1:
                if days_add < len(df.loc[peak_index:peak_indixes[i + 1]]):
                    days_add = len(df.loc[peak_index:peak_indixes[i + 1]])
            else:
                if days_add < len(df):
                    days_add = len(df)

            y = df_peak_log.loc[df_peak_log.index < peak_index +
                                datetime.timedelta(days=days_add), 'confirmed_peak_log'].rolling(3).median().dropna()
        else:
            # for the second+ outbreak use different number of minimum required days
            days_add = days_other_peak_starts
            # exis if we do not have enough data for an estimation
            if len(df.loc[peak_index:peak_index + datetime.timedelta(days=days_add)]) < days_other_peak_starts:
                return df
            else:
                # if we have more data to estimate second peak then use all of it
                days_other_peak_starts = len(df.loc[peak_index:df.index.max()])
                # if enough data then select y for estimating the trend
                y = df_peak_log.loc[(df_peak_log.index < df_peak_log.index.max()) &
                                    (df_peak_log.index > peak_index), 'confirmed_peak_log'].rolling(3).median().dropna()

        # calculate X as number of days in Y and reshape to fit in LogReg model
        X = (y.index - y.index[0]).days.values.reshape(-1, 1)

        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        X = scaler.fit_transform(X)

        # train LogReg model
        reg = LinearRegression().fit(X, y)

        # predict/estimate trend for 10, 20 and 30, 35 days forward, exit if the trend crosses 0
        for days in [days_pred_start + i for i in [0, 10, 20, 35]]:
            X2 = (range(1, days + len(y)) + max(X)[0]).reshape(-1, 1)
            X2 = scaler.transform(X2)
            trend = reg.predict(X2)
            days_pred = days
            if min(trend) < 0:
                break

        # prepare y2 dataframe using index as a date range between the last date of y+1
        # and last date of y+days_estimated_for
        y2_index = pd.date_range(y.index.min() + datetime.timedelta(days=1),
                                 y.index.max() + datetime.timedelta(days=days_pred))
        y2 = pd.DataFrame(index=y2_index, data=trend, columns=['peak_log_trend'])

        # remove extra negative values (if exist) except the first one (for clarity)
        try:
            first_negative_val = y2.loc[y2.peak_log_trend < 0].index[0]
            y2 = y2.loc[y2.index <= first_negative_val, 'peak_log_trend']
        except:
            pass
        # in case its the first peak simply merge DFs
        if i == 0:
            df = df.join(y2, how='outer')
        # otherwise merge and make sure that we fit all trends in the same column for easy plotting
        else:
            df = pd.merge(df, y2, left_index=True, right_index=True, how='outer', suffixes=('_x', '_y'))
            df['peak_log_trend'] = df.loc[:, ['peak_log_trend_x', 'peak_log_trend_y']].apply(
                lambda row: row[0] if pd.isnull(row[0]) == False else row[1], axis=1)
            df.drop(['peak_log_trend_x', 'peak_log_trend_y'], axis=1, inplace=True)

    return df


def add_variables_covid(df, column='confirmed', population=False):

    # df.loc[df[column] == 0, column] = np.NaN
    df.loc[df[column] < 0, column] = 0

    df = add_lag(df, column, 1)

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
        df[f'{column}_active_cases_change'] = df[f'{column}_active_cases'] - df[f'{column}_active_cases'].shift(1)
        df.loc[:, f'{column}_peak_log'] = np.log((df[f'{column}'] / df[f'{column}'].shift(12)).replace({0: np.NaN}))

        df.loc[:, f'{column}_active_cases_avg7'] = np.round(df.loc[:, f'{column}_active_cases'].rolling(7, win_type='triang') .mean(),0)
        df = add_lag(df, f'{column}_active_cases_avg7', 1)

        # A peak is when 7 day average is declining 3 days in a row
        df.loc[:, f'{column}_peak_date'] = 0
        decreasing_day_counter, increasing_day_counter = 0, 0
        peak_value_decrease = 0
        peak_days_threshold = 7
        peak_status = -1  # Epidemic has started
        df.loc[df.index.min(), f'{column}_peak_date'] = -1  # Start of the initial Epidemic
        for row in df.loc[:, [f'{column}_active_cases_avg7', f'{column}_active_cases_avg7_l1']].itertuples():
            if row[1] < row[2]:
                # counting days that average cases are dropping
                decreasing_day_counter += 1
                increasing_day_counter = 0
            else:
                # counting days that average cases are increasing
                increasing_day_counter += 1
                decreasing_day_counter = 0
            # if decreasing for longer than threshold
            if decreasing_day_counter >= peak_days_threshold:
                # take index 7 days before for the start of the trend
                peak_index = row[0] - datetime.timedelta(days=peak_days_threshold)
                peak_value_new = df.loc[peak_index, f'{column}_active_cases_avg7']
                # and if the new peak value is higher than the ond one = so we don't spam decreasing trends
                if peak_value_new > peak_value_decrease:
                    df.loc[peak_index, f'{column}_peak_date'] = 1
                    peak_value_decrease = peak_value_new
                    peak_status += 1
            # if increasing for longer than threshold
            elif increasing_day_counter >= peak_days_threshold:
                # take index 7 days before for the start of the trend
                peak_end_index = row[0] - datetime.timedelta(days=peak_days_threshold)
                # If the peak has been reached in the past we can assign the beginning of new wave
                if peak_status == 0:
                    df.loc[peak_end_index, f'{column}_peak_date'] = -1
                    peak_status -= 1

        # Dropping technical columns
        df.drop([
                 f'{column}_active_cases_avg7',
                 f'{column}_active_cases_avg7_l1',
                 ], axis=1, inplace=True)

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
