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


def plot_line(df, columns, date_cutoff=False, resample=False, title="",
              log_x=False, log_y=False, figsize=(20, 5)):
    """

    :param df:
    :param columns:
    :param date_cutoff:
    :param resample: For example: W-MON
    :return:
    """
    if date_cutoff:
        df = df.loc[df.index >= date_cutoff, columns].copy()
    else:
        df = df.loc[:, columns].copy()

    if resample:
        df = df.resample(resample).mean()

    plt.figure(figsize=figsize)
    plt.xticks(rotation=45)

    palette = sns.color_palette("mako_r", len(columns))  # Set2
    ax = sns.lineplot(data=df, markers=True, dashes=False, palette=palette)
    ax.set(xticks=df.index)
    ax.set(title=title)

    if log_x:
        ax.set_xscale('log')
    if log_y:
        ax.set_yscale('log')

    if date_cutoff:
        years_fmt = mdates.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(years_fmt)

        highlight_weekends(df, ax)


def plot_bar(df, columns=list, date_cutoff=False,title=""):
    plt.figure(figsize=(20, 5))
    plt.xticks(rotation=45)

    if date_cutoff:
        df = df.loc[df.index >= date_cutoff]
        df['dates'] = df.index.date
        ax = sns.barplot(x='dates', y=columns, hue='weekend', data=df).set_title(title)
    else:
        df['dates'] = df.index
        ax = sns.barplot(x='dates', y=columns, data=df).set_title(title)


