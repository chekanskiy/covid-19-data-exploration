from numpy import log10, datetime64, dtype
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.validators.scatter.marker import SymbolValidator


def plot_lines_plotly(df_unfiltered, lands, column, title=False, show_doubling=True, doubling_days=7, showlegend=False):

    df = df_unfiltered.loc[df_unfiltered.land.isin(lands), ['land', column]].dropna()  # .sort_values('confirmed_change')

    _doubling_column = f'double_x{doubling_days}'

    if show_doubling:
        def double_every_x_days(day, days_doubling, start_value=1):
            r = start_value * 2 ** (day / days_doubling)
            return r

        date_range = pd.date_range(df_unfiltered.dropna().index.min(), df_unfiltered.dropna().index.max())
        df_index = pd.DataFrame(columns=['date', 'land', column],
                                data={'date': date_range, 'land': _doubling_column},
                                )
        df_index['rn'] = df_index.groupby('land')['date'].rank(method='first', ascending=True)
        df_index[column] = df_index['rn'].apply(lambda x: double_every_x_days(x, doubling_days))
        df_index['date'] = df_index['date'].astype('datetime64[ns]')
        df_index.set_index('date', inplace=True, drop=False)
        df_index.sort_index(inplace=True, ascending=True)
        del df_index['rn']
        # del df_index['date']
        df = df.append(df_index, ignore_index=False, verify_integrity=False, sort=True)
        # df = df.rename_axis('dates_index').sort_values(by=['land', 'dates_index'], ascending=[True, True])

    del df_unfiltered

    # Create traces
    fig = go.Figure()

    _labels = df['land'].unique()

    #     max_x_range = len(df.index)
    _max_y_range = df.loc[df.land != _doubling_column, column].max()

    _colors = plotly.colors.diverging.Temps * 3  # ['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']
    _symbols = [x for i, x in enumerate(SymbolValidator().values) if i % 2 != 0]  # all markers
    _gray_color = 'rgb(204, 204, 204)'

    _mode_size = [8] * len(_labels)  # [8, 8, 12, 8]
    _line_size = [1] * len(_labels)  # [2, 2, 4, 2]

    for i, l in enumerate(_labels):
        # Adding Doubling x7 line
        if l == _doubling_column:
            fig.add_trace(go.Scatter(x=df.loc[df.land == l].index,
                                     y=df.loc[df.land == l, column],
                                     mode='lines',
                                     marker=dict(color=_gray_color,
                                                 size=_mode_size[i] - 2,
                                                 opacity=0.7,
                                                 symbol=_symbols[i + 2],
                                                 line=dict(
                                                     color=_colors[i],
                                                     width=1
                                                 )
                                                 ),
                                     name=l,
                                     line=dict(color=_gray_color,
                                               width=_line_size[i],
                                               dash='dot', ),
                                     connectgaps=True,
                                     ))

        # Adding all other lines
        else:
            fig.add_trace(go.Scatter(x=df.loc[df.land == l].index,
                                     y=df.loc[df.land == l, column],
                                     mode='lines+markers',
                                     marker=dict(color=_colors[i],
                                                 size=_mode_size[i] - 3,
                                                 opacity=0.7,
                                                 symbol=_symbols[i + 2],
                                                 line=dict(
                                                     color=_colors[i],
                                                     width=1
                                                 )
                                                 ),
                                     name=l,
                                     line=dict(color=_colors[i],
                                               width=_line_size[i]),
                                     connectgaps=False,
                                     ))

            # endpoints
            min_index, max_index = df.loc[df.land == l].index.min(), df.loc[df.land == l].index.max()
            fig.add_trace(go.Scatter(
                x=[min_index, max_index],
                y=[df.loc[(df.index == min_index) & (df.land == l)], df.loc[(df.index == max_index) & (df.land == l)]],
                mode='markers',
                name=l,
                marker=dict(color=_colors[i], size=_mode_size[i] + 2, ),
                showlegend=False,
            ))

    # BUTTONS Changing Y Scale
    updatemenus = list([
        dict(active=1,
             direction="left",
             buttons=list([
                 dict(label='Log',
                      method='update',
                      args=[{'visible': [True, True]},
                            {  # 'title': 'Log scale',
                                'yaxis': {'type': 'log', 'range': [0, log10(_max_y_range)],
                                          'showgrid': False,
                                          'zeroline': False,
                                          'showline': False,
                                          'linecolor': '#1f2630',
                                          }}
                            ]
                      ),
                 dict(label='Linear',
                      method='update',
                      args=[{'visible': [True, True]},
                            {  # 'title': 'Linear scale',
                                'yaxis': {'type': 'linear', 'range': [0, _max_y_range],
                                          # 'showticklabels': False,
                                          'showgrid': False,
                                          'zeroline': False,
                                          'showline': False,
                                          'linecolor': '#1f2630',
                                          }}
                            ]
                      ),
             ]),
             type='buttons',
             pad={"r": 10, "t": 10},
             showactive=True,
             x=0.10,
             xanchor="left",  # ['auto', 'left', 'center', 'right']
             y=1,
             yanchor='top',  # ['auto', 'top', 'middle', 'bottom']
             )
    ])

    # UPDATE LAYOUT, Axis, Margins, Size, Legend, Background
    fig.update_layout(
        updatemenus=updatemenus,
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor=_gray_color,
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='#2cfec1',  # 'rgb(82, 82, 82)',
            ),
            #                 range=[0,max_x_range],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(color='#2cfec1'),
            range=[0, _max_y_range],
        ),
        margin=dict(
            autoexpand=True,
            l=10,
            r=10,
            t=10,
            b=100,
        ),
        showlegend=showlegend,
        legend_orientation="v",
        legend=dict(
            x=1.05,
            y=0, ),
        paper_bgcolor="#1f2630",  # "#F4F4F8",
        plot_bgcolor="#1f2630",  # 'white'
        font=dict(color='#2cfec1'),
        autosize=True,
        # width=800,
        # height=500,
    )

    # ANNOTATIONS
    annotations = []
    # Adding labels
    for i, l in enumerate(_labels):
        min_index, max_index = df.loc[df.land == l].index.min(), df.loc[df.land == l].index.max()
        if l == _doubling_column:
            # labeling x7 line
            x = (min_index + (max_index - min_index) / 2)
            try:
                x = str(x.date())
            except:
                pass
            y = df.loc[(df.land == l) & (df.index == x), column].values[0]
            annotations.append(dict(xref='x', x=x, y=y,
                                    xanchor='center', yanchor='middle',
                                    text="double every 7 days",
                                    font=dict(family='Arial',
                                              size=12,
                                              color=_gray_color, ),
                                    showarrow=False))
        else:
            # labeling the left_side of the plot
            #     y = df.loc[(df.land == l) & (df.index == min_index), column].values[0]
            #     annotations.append(dict(xref='paper', x=0.07, y=y,
            #                                   xanchor='right', yanchor='middle',
            #                                   text=col + ' {}'.format(y),
            #                                   font=dict(family='Arial',
            #                                             size=10),
            #                                   showarrow=False))

            # labeling the right_side of the plot
            y = df.loc[(df.land == l) & (df.index == max_index), column].values[0]
            annotations.append(dict(xref='paper',
                                    x=0.95,
                                    y=y,
                                    xanchor='left', yanchor='middle',
                                    text=l,  # f"{col}: {int(y)}",
                                    font=dict(family='Arial',
                                              size=12,
                                              color=_colors[i]),
                                    showarrow=False))

    # Title
    if title:
        annotations.append(dict(xref='paper', yref='paper', x=0, y=1,
                                xanchor='left', yanchor='bottom',
                                text=title,
                                font=dict(family='Garamond',
                                          size=30,
                                          color='#7fafdf' #'rgb(37,37,37)'
                                          ),
                                showarrow=False))
    # Source
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.06,
                            xanchor='center', yanchor='top',
                            text="<a href='https://www.rki.de/'> Data Source: Robert Koch Institute</a><br><i><a href='https://www.linkedin.com/in/sergeychekanskiy'>Charts: Sergey Chekanskiy</a></i>",
                            font=dict(family='Arial',
                                      size=12,
                                      color='#7fafdf'),
                            showarrow=False))

    fig.update_layout(annotations=annotations)

    return fig
