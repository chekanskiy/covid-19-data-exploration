import pandas as pd
import geopandas as gpd
import pathlib
import sys
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from plotly import colors

from dash.dependencies import Input, Output

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

from func_features import join_series_day_since, join_series_date
from chart_line_animated1 import plot_lines_plotly_animated
from chart_choropleth1 import plot_map_express, plot_map_go
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
geojson = json.load(open('data_geo_de.json', 'r'))

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],)
# external_stylesheets=external_stylesheets)
# '#111111'
COLORS = {
    'background': '#1f2630',
    'text': '#2cfec1',
    # 'charts': colors.diverging.Temps * 3
    'charts': colors.diverging.Temps * 3,  # 'YlGnBu',
    'map': colors.sequential.PuBu  # 'YlGnBu',
}

BASE_FIGURE = dict(
                data=[dict(x=0, y=0)],
                layout=dict(
                    paper_bgcolor=COLORS['background'],
                    plot_bgcolor=COLORS['background'],
                    autofill=True,
                    margin=dict(t=75, r=50, b=100, l=50),
                            ),
                    )

FEATURE_DROP_DOWN = {
    "confirmed_change": "Cases: Daily",
    "confirmed": "Cases: Total",
    "confirmed_active_cases": "Cases: Active",
    "confirmed_change_per_100k": "Cases: Daily per 100k of Population",
    "confirmed_change_pct_3w": "Cases: Daily as % of Rolling 3 Week Sum",
    "confirmed_doubling_days_3w_avg3": "Cases: Days to Double Rolling 3 Week Sum",
    "dead_change": "Deaths: Daily",
    "dead": "Deaths: Total",
    "dead_change_per_100k": "Deaths: Daily per 100k of Population",
    "dead_doubling_days": "Deaths: Days to Double Total Number",
}

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
                                html.Div(children=[
                                    html.Div(
                                        id='button-weekly-on',
                                        children=dbc.Button(children="7 Day Avg Off/On",
                                                            id='button-weekly', size='sm', color="info"),
                                        style={'display': 'inline-block',
                                               'margin-right': 23, 'margin-left': 23,
                                               }),
                                    html.Div(html.P(
                                        children="Daily Confirmed Cases per 100k of Population",
                                        id="heatmap-title",),
                                        style={'display': 'inline-block',
                                               'margin-right': 0, 'margin-left': 0,
                                               }),
                                    # html.Div(
                                    #     # html.P(
                                    #     # children="weekly rolling average",
                                    #     # id="heatmap-states",),
                                    #     id='button-daily-on',
                                    #     children=dbc.Button(
                                    #         html.Span(["Daily", html.I(className="fas fa-plus-circle ml-2")]),
                                    #         color='primary', disabled=True),
                                                ],
                                        ),
                                dcc.Graph(
                                    id='left-main-chart',
                                    figure=BASE_FIGURE
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
                            options=[{'label': l, 'value': v} for l,v in zip(FEATURE_DROP_DOWN.values(), FEATURE_DROP_DOWN.keys())],
                            value="confirmed_change",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=BASE_FIGURE,
                        ),
                            ],
                    # style={'height': '100%', 'width': '100%',
                    #         'margin-right': 0, 'margin-left': 0,
                    #         }
)
                ]
                    )
    ])


@app.callback(
    Output("button-weekly", "children"),
    [Input("button-weekly-on", "n_clicks")])
def update_weekly_button(n_clicks):
    if n_clicks is None or n_clicks % 2 == 0:
        return "7 DAY AVG IS ON"
    else:
        return "7 DAY AVG IS OFF"


@app.callback(
    Output('left-main-chart', 'figure'),
    [Input('chart-dropdown', 'value'),
     Input('dropdown-states', 'value'),
     Input("button-weekly-on", "n_clicks")
    ])
def update_left_main_chart(selected_column, selected_states, n_clicks):
    if n_clicks is None or n_clicks%2==0:
        df = df_rki_orig.copy()
        ro = df.groupby('land').rolling(7, on='date').mean().reset_index(drop=False).loc[:,
             ['date', 'land', selected_column]]
        df = df.merge(ro, on=['date', 'land'],  suffixes=('', '_weekly')).round(3)
        selected_column += '_weekly'
    else:
        df = df_rki_orig
    if len(selected_states) > 0:
        figure = plot_lines_plotly(
            df, selected_states, selected_column,
            show_doubling=True, doubling_days=7, showlegend=False,
            _colors=COLORS['charts'])
    else:
        figure = BASE_FIGURE

    return figure


# @app.callback(
#     Output('selected-data', 'figure'),
#     [Input('chart-dropdown', 'value'),
#     Input('dropdown-states', 'value')
#     ])
# def update_right_main_chart(selected_column, selected_states):
#     if len(selected_states) > 0:
#         figure = plot_box_plotly_static(df_rki_orig, selected_column, selected_states)
#     else:
#         figure = BASE_FIGURE
#
#     return figure


@app.callback(
    Output('selected-data', 'figure'),
    [Input('chart-dropdown', 'value'),
    ])
def update_right_main_chart_map(selected_column):
    df = df_rki_orig.loc[:, [selected_column, 'land', 'iso_code', 'date']].set_index('date', drop=False)
    df = df.loc[df.index == df.index.max()]
    figure = plot_map_go(df, geojson, selected_column, _colors=COLORS['map'])

    return figure


@app.callback(
    Output('heatmap-title', 'children'),
    [Input('chart-dropdown', 'value'),
    ])
def update_main_chart_title(selected_column):

    return FEATURE_DROP_DOWN[selected_column]


# @app.callback(
#     Output('heatmap-states', 'children'),
#     [Input('dropdown-states', 'value')
#     ])
# def update_main_chart_title_states(selected_states):
#
#     return ",  ".join([f"{k} = {s}" for k, s in zip(STATES.keys(), STATES.values()) if s in selected_states])


if __name__ == '__main__':
    app.run_server(debug=True)