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
        ax.axvspan(t0, t1, facecolor="blue", edgecolor="none", alpha=0.2)
    return ax


def plot_line(
    df,
    columns,
    date_cutoff=False,
    resample=False,
    title="",
    log_x=False,
    log_y=False,
    figsize=(20, 5),
):
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
    plt.xticks(rotation=90)

    palette = sns.color_palette("mako_r", len(columns))  # Set2
    ax = sns.lineplot(data=df, markers=True, dashes=False, palette=palette)
    ax.set(xticks=df.index)
    ax.set(title=title)

    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")

    if date_cutoff:
        years_fmt = mdates.DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(years_fmt)

        highlight_weekends(df, ax)

    return ax


def plot_bar(df, columns, date_cutoff=False, title="", figsize=(20, 5)):
    plt.figure(figsize=figsize)
    plt.xticks(rotation=90)

    if date_cutoff:
        df = df.loc[df.index >= date_cutoff]
        df["dates"] = df.index.date
        ax = sns.barplot(x="dates", y=columns, hue="weekend", data=df).set_title(title)
    else:
        df["dates"] = df.index
        ax = sns.barplot(x="dates", y=columns, data=df).set_title(title)


def plot_peak(
    df, columns, date_cutoff=False, title="", log_x=False, log_y=False, figsize=(20, 5)
):
    import seaborn as sns
    import matplotlib.pyplot as plt

    df = df.loc[df.index >= date_cutoff, columns].copy()
    first_negative_val = (
        df.loc[df.confirmed_peak_pred < 0, ["confirmed_peak_pred"]].head(1).index.date
    )
    df.columns = ["actual", "forecast"]

    plt.figure(figsize=figsize)
    plt.xticks(rotation=90)

    #     palette = sns.cubehelix_palette(len(columns), start=0.5, rot=0.1, dark=0, light=.5, reverse=False)
    # sns.color_palette("Set2", len(columns))  # Set2
    #     sns.palplot(palette)
    palette = sns.color_palette("mako_r", len(columns))  # Set2
    ax = sns.lineplot(data=df, markers=True, dashes=False, palette=palette)
    #     ax = sns.lineplot(data=df['confirmed_peak'], color='orange')
    #     ax = sns.lineplot(data=df['confirmed_peak_pred'], color='blue', linewidth=2)

    ax1 = ax.axes
    ax1.axhline(0, ls="-", linewidth=1.5, color="gray")
    ax1.axvline(first_negative_val, ls="--", linewidth=1.5, color="gray")

    ax.set(xticks=df.index)
    ax.set(title=title)

    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")


def print_charts_country(df, region, date_cutoff="2020-03-15", figsize=(20, 5)):
    plot_bar(
        df,
        columns="confirmed",
        title=f"{region}: Total Cases",
        date_cutoff=date_cutoff,
        figsize=figsize,
    )
    plot_bar(
        df,
        columns="confirmed_change",
        title=f"{region}: Daily Cases",
        date_cutoff=date_cutoff,
        figsize=figsize,
    )
    plot_bar(
        df,
        title=f"{region}: Active Cases",
        columns="confirmed_active_cases",
        date_cutoff=date_cutoff,
        figsize=figsize,
    )
    plot_line(
        df,
        title=f"{region}: Daily Cases Change, %",
        columns=["confirmed_change_pct", "confirmed_change_pct_3w"],
        date_cutoff=date_cutoff,
        figsize=figsize,
    )
    plot_line(
        df,
        title=f"{region}: Doubling Days, Confirmed",
        columns=["confirmed_doubling_days", "confirmed_doubling_days_3w_avg3"],
        date_cutoff=date_cutoff,
        figsize=figsize,
    )
    plot_line(
        df,
        title=f"{region}: Doubling Days, Dead",
        columns=["dead_doubling_days", "dead_doubling_days_3w_avg3"],
        date_cutoff=date_cutoff,
        figsize=figsize,
    )


def plot_lines_plotly(df, title, show_doubling=True, doubling_days=7, showlegend=False):
    import plotly.graph_objects as go
    from plotly.validators.scatter.marker import SymbolValidator

    doubling_column = f"double_x{doubling_days}"
    if show_doubling:

        def double_every_x_days(day, days_doubling):
            d = np.ceil(day / days_doubling)
            r = 1 * 2 ** (day / days_doubling)
            return r

        df["day"] = df.index
        df[doubling_column] = df["day"].apply(
            lambda x: double_every_x_days(x, doubling_days)
        )
        del df["day"]

    # Create traces
    fig = go.Figure()

    labels = [c for c in df.columns if c != doubling_column]
    max_y_range = int(max(df.loc[:, labels].max()) * 1.1)
    #     max_x_range = len(df.index)
    colors = (
        plotly.COLORS.sequential.Viridis + plotly.COLORS.sequential.Viridis
    )  # 10 colors #['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']
    symbols = [
        x for i, x in enumerate(SymbolValidator().values) if i % 2 != 0
    ]  # all markers
    # print(len(labels))
    # print(len(colors))
    gray_color = "rgb(204, 204, 204)"

    mode_size = [8] * len(df.columns)  # [8, 8, 12, 8]
    line_size = [1] * len(df.columns)  # [2, 2, 4, 2]

    for i, col in enumerate(df.columns):
        # Adding Doubling x7 line
        if col == doubling_column:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines",
                    marker=dict(
                        color=gray_color,
                        size=mode_size[i] - 2,
                        opacity=0.7,
                        symbol=symbols[i + 2],
                        line=dict(color=colors[i], width=1),
                    ),
                    name=col,
                    line=dict(color=gray_color, width=line_size[i], dash="dot",),
                    connectgaps=True,
                )
            )

        # Adding all other lines
        else:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines+markers",
                    marker=dict(
                        color=colors[i],
                        size=mode_size[i] - 3,
                        opacity=0.7,
                        symbol=symbols[i + 2],
                        line=dict(color=colors[i], width=1),
                    ),
                    name=col,
                    line=dict(color=colors[i], width=line_size[i]),
                    connectgaps=False,
                )
            )

            # endpoints
            fig.add_trace(
                go.Scatter(
                    x=[min(df[col].dropna().index), max(df[col].dropna().index)],
                    y=[
                        df.loc[min(df[col].dropna().index), col],
                        df.loc[max(df[col].dropna().index), col],
                    ],
                    mode="markers",
                    name=col,
                    marker=dict(color=colors[i], size=mode_size[i] + 2,),
                    showlegend=False,
                )
            )

    # BUTTONS Changing Y Scale
    updatemenus = list(
        [
            dict(
                active=1,
                buttons=list(
                    [
                        dict(
                            label="Log Scale",
                            method="update",
                            args=[
                                {"visible": [True, True]},
                                {
                                    "title": "Log scale",
                                    "yaxis": {
                                        "type": "log",
                                        "range": [0, np.log10(max_y_range)],
                                    },
                                },
                            ],
                        ),
                        dict(
                            label="Linear Scale",
                            method="update",
                            args=[
                                {"visible": [True, False]},
                                {
                                    "title": "Linear scale",
                                    "yaxis": {
                                        "type": "linear",
                                        "range": [0, max_y_range],
                                        "showticklabels": False,
                                    },
                                },
                            ],
                        ),
                        dict(label="Play", method="animate", args=[None]),
                    ]
                ),
            )
        ]
    )

    # UPDATE LAYOUT, Axis, Margins, Size, Legend, Background
    fig.update_layout(
        updatemenus=updatemenus,
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor=gray_color,
            linewidth=2,
            ticks="outside",
            tickfont=dict(family="Arial", size=12, color="rgb(82, 82, 82)",),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            range=[0, max_y_range],
        ),
        autosize=False,
        margin=dict(autoexpand=True, l=150, r=30, t=110, b=90,),
        showlegend=showlegend,
        legend_orientation="v",
        legend=dict(x=1.1, y=0,),
        plot_bgcolor="white",
        width=1200,
        height=900,
    )

    # ANNOTATIONS
    annotations = []
    # Adding labels
    for i, col in enumerate(df.columns):
        if col == doubling_column:
            # labeling x7 line
            y = 52  # df.loc[int(max(df.index/2)), 'x7']
            x = 40  # int(max(df.index)/2)
            annotations.append(
                dict(
                    xref="x",
                    x=x,
                    y=y,
                    xanchor="center",
                    yanchor="middle",
                    text="double every 7 days",
                    font=dict(family="Arial", size=12, color=gray_color,),
                    showarrow=False,
                )
            )
            continue

        # labeling the left_side of the plot
        #     y = df.loc[min(df[col].dropna().index),col]
        #     annotations.append(dict(xref='paper', x=0.07, y=y,
        #                                   xanchor='right', yanchor='middle',
        #                                   text=col + ' {}'.format(y),
        #                                   font=dict(family='Arial',
        #                                             size=10),
        #                                   showarrow=False))

        # labeling the right_side of the plot
        x = max(df[col].dropna().index)
        y = df.loc[max(df[col].dropna().index), col]
        annotations.append(
            dict(
                xref="paper",
                x=0.95,
                y=y,
                xanchor="left",
                yanchor="middle",
                text=f"{col}: {int(y)}",
                font=dict(family="Arial", size=12),
                showarrow=False,
            )
        )

    # Title
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            xanchor="left",
            yanchor="bottom",
            text=title,
            font=dict(family="Garamond", size=30, color="rgb(37,37,37)"),
            showarrow=False,
        )
    )
    # Source
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.1,
            xanchor="center",
            yanchor="top",
            text="Source: Robert Koch Institute & " + "Storytelling with data",
            font=dict(family="Arial", size=12, color="rgb(150,150,150)"),
            showarrow=False,
        )
    )

    fig.update_layout(annotations=annotations)

    fig.show()


def plot_lines_plotly_animated(
    df, title, show_doubling=True, doubling_days=7, showlegend=False
):
    import plotly.graph_objects as go
    from plotly.validators.scatter.marker import SymbolValidator

    doubling_column = f"double_x{doubling_days}"
    if show_doubling:

        def double_every_x_days(day, days_doubling):
            d = np.ceil(day / days_doubling)
            r = 1 * 2 ** (day / days_doubling)
            return r

        df["day"] = df.index
        df[doubling_column] = df["day"].apply(
            lambda x: double_every_x_days(x, doubling_days)
        )
        del df["day"]

    # Create traces
    fig = go.Figure()

    labels = [c for c in df.columns if c != doubling_column]
    max_y_range = int(max(df.loc[:, labels].max()) * 1.1)
    #     max_x_range = len(df.index)
    colors = (
        plotly.COLORS.sequential.Viridis + plotly.COLORS.sequential.Viridis
    )  # 10 colors #['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']
    symbols = [
        x for i, x in enumerate(SymbolValidator().values) if i % 2 != 0
    ]  # all markers
    # print(len(labels))
    # print(len(colors))
    gray_color = "rgb(204, 204, 204)"
    days = df.index
    animation_speed = 50

    mode_size = [8] * len(df.columns)  # [8, 8, 12, 8]
    line_size = [1] * len(df.columns)  # [2, 2, 4, 2]

    for i, col in enumerate(df.columns):
        # Adding Doubling x7 line
        if col == doubling_column:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines",
                    marker=dict(
                        color=gray_color,
                        size=mode_size[i] - 2,
                        opacity=0.7,
                        symbol=symbols[i + 2],
                        line=dict(color=colors[i], width=1),
                    ),
                    name=col,
                    line=dict(color=gray_color, width=line_size[i], dash="dot",),
                    connectgaps=True,
                )
            )

        # Adding all other lines
        else:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines+markers",
                    marker=dict(
                        color=colors[i],
                        size=mode_size[i] - 3,
                        opacity=0.7,
                        symbol=symbols[i + 2],
                        line=dict(color=colors[i], width=1),
                    ),
                    name=col,
                    line=dict(color=colors[i], width=line_size[i]),
                    connectgaps=False,
                )
            )

    #                 # endpoints
    #                 fig.add_trace(go.Scatter(
    #                                         x=[min(df[col].dropna().index), max(df[col].dropna().index)],
    #                                         y=[df.loc[min(df[col].dropna().index), col], df.loc[max(df[col].dropna().index), col]] ,
    #                                         mode='markers',
    #                                         name=col,
    #                                         marker=dict(color=colors[i], size=mode_size[i] + 2,),
    #                                         showlegend=False,
    #                 ))

    # BUTTONS Changing Y Scale
    updatemenus = list(
        [
            dict(
                active=1,
                buttons=list(
                    [
                        dict(
                            label="Scale: Log",
                            method="update",
                            args=[
                                {"visible": [True, True]},
                                {
                                    "title": "Log scale",
                                    "yaxis": {
                                        "type": "log",
                                        "range": [0, np.log10(max_y_range)],
                                    },
                                },
                            ],
                        ),
                        dict(
                            label="Scale: Linear",
                            method="update",
                            args=[
                                {"visible": [True, False]},
                                {
                                    "title": "Linear scale",
                                    "yaxis": {
                                        "type": "linear",
                                        "range": [0, max_y_range],
                                        "showticklabels": False,
                                    },
                                },
                            ],
                        ),
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {
                                        "duration": animation_speed,
                                        "redraw": False,
                                    },
                                    "fromcurrent": True,
                                    "transition": {
                                        "duration": animation_speed * 0.8,
                                        "easing": "quadratic-in-out",
                                    },
                                },
                            ],
                        ),
                        dict(
                            args=[
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0},
                                },
                            ],
                            label="Pause",
                            method="animate",
                        ),
                    ]
                ),
                type="buttons",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=-0.15,
                xanchor="left",  # ['auto', 'left', 'center', 'right']
                y=0.8,
                yanchor="bottom",  # ['auto', 'top', 'middle', 'bottom']
            )
        ]
    )

    # ===== SLIDER AND FRAMES ==================================================================
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Day:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": animation_speed, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }

    # ==== MAKE FRAMES ========================================================================
    frames_list = list()
    for day in df.index:
        frame = go.Frame(data=[], name=str(day))
        data_list = []
        for label in labels:
            dataset_by_day_label = df.loc[min(df.index) : day, label]
            data_dict = {
                "x": list(dataset_by_day_label.index),  # list(day),
                "y": list(dataset_by_day_label.values),
                "mode": "lines+markers",
                "text": list(label),
                #                 "marker": {
                #                     "sizemode": "area",
                # #                     "sizeref": 200000,
                #                     "size": list(dataset_by_day_label.values)
                #                 },
                #                 "name": label
            }
            data_list.append(data_dict)
            frame["data"] = data_list
        frames_list.append(frame)

        slider_step = {
            "args": [
                [day],
                {
                    "frame": {"duration": animation_speed, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": animation_speed},
                },
            ],
            "label": day,
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)

    fig["frames"] = frames_list

    #     fig_dict["layout"]["sliders"] = [sliders_dict]
    # ===== END SLIDER AND FRAMES =====

    # ===== UPDATE LAYOUT, Axis, Margins, Size, Legend, Background =========================
    fig.update_layout(
        updatemenus=updatemenus,
        sliders=[sliders_dict],
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor=gray_color,
            linewidth=2,
            ticks="outside",
            tickfont=dict(family="Arial", size=12, color="rgb(82, 82, 82)",),
            #                 range=[0,max_x_range],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            range=[0, max_y_range],
        ),
        autosize=False,
        margin=dict(autoexpand=True, l=150, r=30, t=110, b=90,),
        showlegend=showlegend,
        legend_orientation="v",
        legend=dict(x=1.1, y=0,),
        plot_bgcolor="white",
        width=1200,
        height=900,
    )

    # ANNOTATIONS
    annotations = []
    # Adding labels
    for i, col in enumerate(df.columns):
        if col == doubling_column:
            # labeling x7 line
            y = 52  # df.loc[int(max(df.index/2)), 'x7']
            x = 40  # int(max(df.index)/2)
            annotations.append(
                dict(
                    xref="x",
                    x=x,
                    y=y,
                    xanchor="center",
                    yanchor="middle",
                    text="double every 7 days",
                    font=dict(family="Arial", size=12, color=gray_color,),
                    showarrow=False,
                )
            )
            continue

        # labeling the left_side of the plot
        #     y = df.loc[min(df[col].dropna().index),col]
        #     annotations.append(dict(xref='paper', x=0.07, y=y,
        #                                   xanchor='right', yanchor='middle',
        #                                   text=col + ' {}'.format(y),
        #                                   font=dict(family='Arial',
        #                                             size=10),
        #                                   showarrow=False))

        # labeling the right_side of the plot
        x = max(df[col].dropna().index)
        y = df.loc[max(df[col].dropna().index), col]
        annotations.append(
            dict(
                xref="paper",
                x=0.95,
                y=y,
                xanchor="left",
                yanchor="middle",
                text=f"{col}: {int(y)}",
                font=dict(family="Arial", size=12),
                showarrow=False,
            )
        )

    # Title
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            xanchor="left",
            yanchor="bottom",
            text=title,
            font=dict(family="Garamond", size=30, color="rgb(37,37,37)"),
            showarrow=False,
        )
    )
    # Source
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.1,
            xanchor="center",
            yanchor="top",
            text="Source: Robert Koch Institute & " + "Storytelling with data",
            font=dict(family="Arial", size=12, color="rgb(150,150,150)"),
            showarrow=False,
        )
    )

    fig.update_layout(annotations=annotations)

    fig.show()
