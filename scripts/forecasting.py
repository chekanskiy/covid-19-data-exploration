from fbprophet import Prophet
import datetime
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


def add_forecast_prophet(
    df_in, column, window=60,
):
    df = df_in.loc[:, [column]].dropna()
    df["ds"] = df.index
    df.columns = ["y", "ds"]
    m = Prophet(
        weekly_seasonality=False, daily_seasonality=False, yearly_seasonality=False
    )
    m.fit(df)
    future = m.make_future_dataframe(periods=window)
    forecast = m.predict(future)
    forecast.set_index(forecast.ds, inplace=True)
    forecast = forecast.loc[:, ["yhat", "yhat_lower", "yhat_upper"]]
    df_extra_dates = pd.DataFrame(
        {
            "day": pd.Series(
                [
                    max(df_in.index) + datetime.timedelta(1),
                    max(df_in.index) + datetime.timedelta(window),
                ]
            )
        }
    )
    df_extra_dates.set_index("day", inplace=True)
    df_extra_dates = df_extra_dates.asfreq("D")
    df_in = df_in.append(df_extra_dates)
    df_result = pd.concat([df_in, forecast], axis=1)
    df_result[f"{column}_pred"] = df_result.loc[
        df_result[column].isnull() == True, ["yhat"]
    ]

    return df_result


def add_trend_linear(df, column, date_range, days_add=15):
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import MinMaxScaler

    y = df.loc[
        (df.index >= date_range[0]) & (df.index <= date_range[1]), column
    ].dropna()  # .rolling(3).median().dropna()

    # calculate X as number of days in Y and reshape to fit in LogReg model
    X = (y.index - y.index[0]).days.values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X = scaler.fit_transform(X)

    # train LogReg model
    reg = LinearRegression().fit(X, y)

    # predict/estimate trend for 10, 20 and 30, 35 days forward, exit if the trend crosses 0
    X2 = (range(1, days_add + len(y)) + max(X)[0]).reshape(-1, 1)
    X2 = scaler.transform(X2)
    trend = reg.predict(X2)
    # prepare y2 dataframe using index as a date range between the last date of y+1
    # and last date of y+days_estimated_for
    y2_index = pd.date_range(
        y.index.min() + datetime.timedelta(days=1),
        y.index.max() + datetime.timedelta(days=days_add),
    )
    y2 = pd.DataFrame(index=y2_index, data=trend, columns=[f"{column}_trend"])
    df = df.join(y2, how="outer")
    return df


def add_trend_arima(df, column, date_range, days_add=15, start=None):
    from sklearn.preprocessing import MinMaxScaler
    import statsmodels.api as sm

    if start == None:
        start = df.index.max().date()
    y = df.loc[
        (df.index >= date_range[0]) & (df.index <= date_range[1]), column
    ].dropna()  # .rolling(3).median().dropna()

    # calculate X as number of days in Y and reshape to fit in LogReg model
    X = (y.index - y.index[0]).days.values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X = scaler.fit_transform(X)

    # train LogReg model

    mod = sm.tsa.statespace.SARIMAX(
        y,
        #                                     order=(0, 0, 0),
        #                                     seasonal_order=(0,0,0,0),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    results = mod.fit()

    pred_dynamic = results.get_prediction(
        start=pd.to_datetime(start), dynamic=True, full_results=True
    )
    pred_dynamic_ci = pred_dynamic.conf_int()
    y2 = pred_dynamic.predicted_mean
    y2.rename(f"{column}_trend", inplace=True)
    y2.columns = [f"{column}_trend"]

    # Get forecast 500 steps ahead in future
    pred_uc = results.get_forecast(steps=days_add)
    pred_uc = pred_uc.predicted_mean
    pred_uc.rename(f"{column}_trend", inplace=True)
    pred_uc.columns = [f"{column}_trend"]

    #     print(y2,"\n")
    #     print(pred_uc,"\n")

    print(results.summary().tables[1])
    #     results.plot_diagnostics(figsize=(15, 12))
    #     plt.show()

    df = df.join(y2, how="outer")
    df = pd.merge(
        df,
        pred_uc,
        left_index=True,
        right_index=True,
        how="outer",
        suffixes=("_x", "_y"),
    )
    df[f"{column}_trend"] = df.loc[:, [f"{column}_trend_x", f"{column}_trend_y"]].apply(
        lambda row: row[0] if pd.isnull(row[0]) == False else row[1], axis=1
    )
    df.drop([f"{column}_trend_x", f"{column}_trend_y"], axis=1, inplace=True)

    return df
