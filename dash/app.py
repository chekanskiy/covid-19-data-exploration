import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pathlib
import os, sys

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
sys.path.insert(0, APP_PATH)

from func_features import join_series_day_since
from chart_line_animated1 import plot_lines_plotly_animated
from chart_line_static1 import plot_lines_plotly

YEARS = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]

df_rki = pd.read_csv('data_rki_prepared.csv')
df_rki.set_index('date', inplace=True)

df_rki = join_series_day_since(df_rki, 'confirmed_per_100k', 'confirmed_day_since_10')#.loc[1:, ['Hamburg', 'Bremen', 'Bavaria', 'Berlin',]]

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],)
# external_stylesheets=external_stylesheets)
# '#111111'
colors = {
    'background': '#1f2630',
    'text': '#2cfec1'
}

app.layout = html.Div(
    id="root",
    # style={'backgroundColor': colors['background']},
    children=[
        html.Div(
            id='header',
            children=[
                html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
                html.H4(children='COVID-19 in Germany', #style={ 'textAlign': 'left', 'color': colors['text']}
                       ),
                html.P(
                      id="description",
                      children="† Tracking the progress of COVID-19 pandemic in Germany per State.",
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
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Confirmed Cases per 100k of Population",
                                    id="heatmap-title",
                                ),
                        dcc.Graph(
                            id='county-choropleth',
                            figure=plot_lines_plotly(
                                   df_rki,
                                   "Confirmed Cases per 100k of Population",
                                   show_doubling=True, doubling_days=7, showlegend=False)
                                )
                                    ])
                            ]
                        ),
                html.Div(
                    id="right-column",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        # dcc.Dropdown(
                        #     options=[
                        #         {
                        #             "label": "Histogram of total number of deaths (single year)",
                        #             "value": "show_absolute_deaths_single_year",
                        #         },
                        #         {
                        #             "label": "Histogram of total number of deaths (1999-2016)",
                        #             "value": "absolute_deaths_all_time",
                        #         },
                        #         {
                        #             "label": "Age-adjusted death rate (single year)",
                        #             "value": "show_death_rate_single_year",
                        #         },
                        #         {
                        #             "label": "Trends in age-adjusted death rate (1999-2016)",
                        #             "value": "death_rate_all_time",
                        #         },
                        #     ],
                        #     value="show_death_rate_single_year",
                        #     id="chart-dropdown",
                        # ),
                            ]
                        )
                ]
                    )
    ])

if __name__ == '__main__':
    app.run_server(debug=True)