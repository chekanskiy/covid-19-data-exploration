import pandas as pd
import pathlib
import sys
from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

from func_features import join_series_day_since, join_series_date
from chart_line_animated1 import plot_lines_plotly_animated
from chart_boxplot_static1 import plot_box_plotly_static
from chart_line_static1 import plot_lines_plotly

STATES = {'BW': 'Baden-Wuerttemberg',
          'BY': 'Bavaria',
          'BE': 'Berlin',
          'BB': 'Brandenburg',
          'HB': 'Bremen',
          'HH': 'Hamburg',
          'HE': 'Hesse',
          'NI': 'Lower Saxony',
          'MV': 'Mecklenburg-Western Pomerania',
          'NW': 'North Rhine-Westphalia',
          'RP': 'Rhineland-Palatinate',
          'SL': 'Saarland',
          'SN': 'Saxony',
          'ST': 'Saxony-Anhalt',
          'SH': 'Schleswig-Holstein',
          'TH': 'Thuringia'}

df_rki_orig = pd.read_csv('data_rki_prepared.csv')
df_rki_orig['date'] = df_rki_orig['date'].astype('datetime64[ns]')
df_rki_orig.set_index('date', inplace=True, drop=False)

# df_rki = join_series_day_since(df_rki, 'confirmed_change_per_100k', 'confirmed_day_since_10')
# df_rki = df_rki.rolling(7).mean().round(2).dropna().sort_index()
# .loc[1:, ['Hamburg', 'Bremen', 'Bavaria', 'Berlin',]]

# df_rki = join_series_date(df_rki_orig, 'confirmed_change_per_100k')
# df_rki = df_rki.rolling(7).mean().round(2).dropna().sort_index(ascending=False)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],)
# external_stylesheets=external_stylesheets)
# '#111111'
COLORS = {
    'background': '#1f2630',
    'text': '#2cfec1'
}

BASE_FIGUE = dict(
                data=[dict(x=0, y=0)],
                layout=dict(
                    paper_bgcolor=COLORS['background'],
                    plot_bgcolor=COLORS['background'],
                    autofill=True,
                    margin=dict(t=75, r=50, b=100, l=50),
                            ),
                    )

app.layout = html.Div(
    id="root",
    # style={'backgroundColor': colors['background']},
    children=[
        html.Div(
            id='header',
            children=[
                # html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
                html.H4(children='COVID-19 in Germany', #style={ 'textAlign': 'left', 'color': colors['text']}
                       ),
                html.P(
                      id="description",
                      children="Tracking the progress of COVID-19 pandemic for each federal state",
                  ),
                    ]
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="dropdown-container",
                            children=[
                                html.P(
                                    id="dropdown-text",
                                    children="Change the selection of federal states to display:",
                                ),
                                html.Div(
                                    dcc.Dropdown(
                                        id="dropdown-states",
                                        style={"color": "#7fafdf"},
                                        multi=True,
                                        value=['Hamburg', 'Bremen', 'Berlin'],  # Or single value, like Hamburg
                                        options=[
                                                {
                                                 "label": str(iso),
                                                 "value": str(state),
                                                }
                                                for state, iso in zip(STATES.values(), STATES.keys())],
                                                    ),
                                    style={'width': '100%', 'display': 'inline-block',
                                           'margin-right': 0, 'margin-left': 0,
                                           'virticalalign': 'middle'
                                           }
                                        ),
                                # html.Div(
                                #     [
                                #         html.Span(
                                #                       "?",
                                #                       id="tooltip-target",
                                #                       style={
                                #                              "textAlign": "center",
                                #                              "color": "white"
                                #                       },
                                #                       className="dot"),
                                #
                                #                  dbc.Tooltip("BW: Baden-Wuerttemberg <br>"
                                #                           "BY: Bavaria "
                                #                           "BE: Berlin "
                                #                           "BB: Brandenburg "
                                #                           "HB: Bremen "
                                #                           "HH: Hamburg "
                                #                           "HE: Hesse "
                                #                           "NI: Lower Saxony "
                                #                           "MV: Mecklenburg-Western Pomerania "
                                #                           "NW: North Rhine-Westphalia "
                                #                           "RP: Rhineland-Palatinate "
                                #                           "SL: Saarland "
                                #                           "SN: Saxony "
                                #                           "ST: Saxony-Anhalt "
                                #                           "SH: Schleswig-Holstein "
                                #                           "TH: Thuringia ",
                                #                        target="tooltip-target",
                                #                         placement='bottom'
                                #                  )
                                #     ],
                                #     style={'width': '10%', 'display': 'inline-block',
                                #            'margin-right': 10, 'margin-left': 30,
                                #            'virticalalign': 'middle'
                                #            }
                                #             )

                                # html.Div(dcc.DatePickerRange(
                                #     id='date-picker-range',
                                #     start_date=dt(1997, 5, 3),
                                #     end_date_placeholder_text='Select a date!',
                                # ),
                                #     style={'width': '15%', 'display': 'inline-block', 'margin-left': 10,
                                #            'background-color': 'inherit',
                                #            'virticalalign': 'middle'})
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Daily Confirmed Cases per 100k of Population",
                                    id="heatmap-title",
                                ),
                                html.P(
                                    "weekly rolling average",
                                    id="heatmap-subtitle",
                                ),
                                dcc.Graph(
                                    id='left-main-chart',
                                    figure=BASE_FIGUE
                                         ),
                                # dcc.Loading(
                                #     id="loading-1",
                                #     type="circle",
                                #     children=[
                                #
                                #             ])
                            ])
                            ]
                        ),
                html.Div(
                    id="right-column",
                    children=[
                        html.P(id="chart-selector", children="Change metric to display:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "New Cases: Daily",
                                    "value": "confirmed_change",
                                },
                                {
                                    "label": "New Cases: Daily per 100k of Population",
                                    "value": "confirmed_change_per_100k",
                                },
                                {
                                    "label": "New Cases: Daily as % of Rolling 3 Week Sum",
                                    "value": "confirmed_change_pct_3w",
                                },
                                {
                                    "label": "New Cases: Days to Double Rolling 3 Week Sum",
                                    "value": "confirmed_doubling_days_3w_avg3",
                                },
                                {
                                    "label": "Deaths: Daily",
                                    "value": "dead_change",
                                },
                                {
                                    "label": "Deaths: Daily per 100k of Population",
                                    "value": "dead_change_per_100k",
                                },
                                {
                                    "label": "Deaths: Days to Double Total Number",
                                    "value": "dead_doubling_days",
                                },
                            ],
                            value="confirmed_change",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=BASE_FIGUE,
                        ),
                            ]
                        )
                ]
                    )
    ])


@app.callback(
    Output('left-main-chart', 'figure'),
    [Input('chart-dropdown', 'value'),
     Input('dropdown-states', 'value')
    ])
def update_left_main_chart(selected_column, selected_states):
    if len(selected_states) > 0:
        figure = plot_lines_plotly(
            df_rki_orig, selected_states, selected_column,  show_doubling=True, doubling_days=7, showlegend=False)
    else:
        figure = BASE_FIGUE

    return figure


@app.callback(
    Output('selected-data', 'figure'),
    [Input('chart-dropdown', 'value'),
    Input('dropdown-states', 'value')
    ])
def update_left_main_chart(selected_column, selected_states):
    if len(selected_states) > 0:
        figure = plot_box_plotly_static(df_rki_orig, selected_column, selected_states)
    else:
        figure = BASE_FIGUE

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)