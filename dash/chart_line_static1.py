import numpy as np
import plotly
import plotly.graph_objects as go
from plotly.validators.scatter.marker import SymbolValidator


def plot_lines_plotly(df, title=False, show_doubling=True, doubling_days=7, showlegend=False):
    _doubling_column = f'double_x{doubling_days}'
    if show_doubling:
        def double_every_x_days(day, days_doubling):
            r = 1 * 2 ** (day / days_doubling)
            return r

        df['day'] = range(1, len(df.index) + 1)
        df[_doubling_column] = df['day'].apply(lambda x: double_every_x_days(x, doubling_days))
        del df['day']

    # Create traces
    fig = go.Figure()

    _labels = [c for c in df.columns if c != _doubling_column]

    #     max_x_range = len(df.index)
    try:
        _max_y_range = max(df.loc[:, _labels].max()) * 1.05
    except ValueError:
        _max_y_range = max(df[_doubling_column]) * 1.05

    _colors = plotly.colors.diverging.Temps * 3  # ['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']
    _symbols = [x for i, x in enumerate(SymbolValidator().values) if i % 2 != 0]  # all markers
    _gray_color = 'rgb(204, 204, 204)'

    _mode_size = [8] * len(df.columns)  # [8, 8, 12, 8]
    _line_size = [1] * len(df.columns)  # [2, 2, 4, 2]

    for i, col in enumerate(df.columns):
        # Adding Doubling x7 line
        if col == _doubling_column:
            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col],
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
                                     name=col,
                                     line=dict(color=_gray_color,
                                               width=_line_size[i],
                                               dash='dot', ),
                                     connectgaps=True,
                                     ))

        # Adding all other lines
        else:
            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col],
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
                                     name=col,
                                     line=dict(color=_colors[i],
                                               width=_line_size[i]),
                                     connectgaps=False,
                                     ))

            # endpoints
            fig.add_trace(go.Scatter(
                x=[min(df[col].dropna().index), max(df[col].dropna().index)],
                y=[df.loc[min(df[col].dropna().index), col], df.loc[max(df[col].dropna().index), col]],
                mode='markers',
                name=col,
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
                                'yaxis': {'type': 'log', 'range': [0, np.log10(_max_y_range)],
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
    for i, col in enumerate(df.columns):
        if col == _doubling_column:
            # labeling x7 line
            y = 52  # df.loc[int(max(df.index/2)), 'x7']
            x = 40  # int(max(df.index)/2)
            annotations.append(dict(xref='x', x=x, y=y,
                                    xanchor='center', yanchor='middle',
                                    text="double every 7 days",
                                    font=dict(family='Arial',
                                              size=12,
                                              color=_gray_color, ),
                                    showarrow=False))
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
        # x = max(df[col].dropna().index)
        y = df.loc[max(df[col].dropna().index), col]
        annotations.append(dict(xref='paper',
                                x=0.95,
                                y=y,
                                xanchor='left', yanchor='middle',
                                text=col,  # f"{col}: {int(y)}",
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
