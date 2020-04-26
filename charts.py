import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

sns.set()


def highlight_weekends(df, ax):
    sundays = [i for i, k in zip(df.index, df.index.weekday) if k == 5]
    for i in sundays:
        t0 = i.date()  # datetime.datetime.strptime(i.date(), "%Y-%m-%d")
        t1 = i.date() + datetime.timedelta(days=2)
        ax.axvspan(t0, t1, facecolor='blue', edgecolor='none', alpha=.2)
    return ax


def plot_line(df, columns=list, date_cutoff='2020-03-15'):
    df = df.loc[df.index >= date_cutoff, columns]

    plt.figure(figsize=(20, 5))
    plt.xticks(rotation=45)

    ax = sns.lineplot(data=df)
    ax.set(xticks=df.index.values)

    years_fmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(years_fmt)

    highlight_weekends(df, ax)


def plot_bar(df, column, date_cutoff='2020-03-15'):

    df = df.loc[df.index >= date_cutoff]
    df['dates'] = df.index.date

    plt.figure(figsize=(20, 5))
    plt.xticks(rotation=45)
    ax = sns.barplot(x='dates', y=column, hue='weekend', data=df)