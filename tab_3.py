# Configuração do Dash
import plotly.graph_objects as go # biblioteca plotly, para plots interativos
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, ctx
from dash import Input, Output, State, callback

from model import *

import numpy as np
from uncertainties import unumpy
from uncertainties.umath import *

# Tab-1
# ===

def generate_tab(config, measure_data, exp_data):
    generate_tab.exp_data = exp_data
    fig = go.Figure(
        {'layout' : {'xaxis_title' : 'Tempo (s)',
                     'yaxis_title' : 'Distância (m)',
                     'legend_title' : 'Legenda'
                     }}
    )

    fig.add_trace(go.Scatter(
        name="Dados experimentais",
        visible=True,
        mode="markers",
        marker=dict(color="#4f406d",size=6),
        error_x=dict(
            type='data', # value of error bar given in data coordinates
            visible=True),
        error_y=dict(
            type='data', # value of error bar given in data coordinates
            visible=True)
        )
    )

    fig.add_trace(
        go.Scatter(
            name="Modelagem",
            mode="lines",
            visible=True,
            line=dict(color="#8fa3e8", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            name="Fit não linear",
            mode="lines",
            visible=True,
            line=dict(color="#d2daf5", width=3),
        )
    )

    data_dropdown_options = list(measure_data['experimental-data'].keys())
    data_start_option = config['test-model-tab']['start_option']


    tab = [
        dbc.Row([
            dbc.Col([
                html.H3(["Opções"]),
                html.Br(),
                dcc.Markdown(
                  r'''
                  $d(t) = K_1 \, e^{-C_2 \, t} + \frac{(C_1 C_2 \, t - C_1)}{C_2^2} + K_2$
                  ''', mathjax=True
                ),
                dbc.Row([
                    dbc.Col([dcc.Markdown('$C_1$:', mathjax=True)], width=2),
                    dbc.Col([dcc.Slider(
                        min=-0.1, max=0, value=-0.06, id='tab-3-slider-C1',
                        tooltip={"placement": "bottom", "always_visible": True},
                    )], width=10),
                ]),
                dbc.Row([
                    dbc.Col([dcc.Markdown('$C_2$:', mathjax=True)], width=2),
                    dbc.Col([dcc.Slider(
                        min=-2, max=-1, value=-1, id='tab-3-slider-C2',
                        tooltip={"placement": "bottom", "always_visible": True},
                    )], width=10),
                ]),
                dbc.Row([
                    dbc.Col([dcc.Markdown('$K_1$:', mathjax=True)], width=2),
                    dbc.Col([dcc.Slider(
                        min=-0.01, max=0, value=-0.001, id='tab-3-slider-K1',
                        tooltip={"placement": "bottom", "always_visible": True},
                    )], width=10),
                ]),
                dbc.Row([
                    dbc.Col([dcc.Markdown('$K_2$:', mathjax=True)], width=2),
                    dbc.Col([dcc.Slider(
                        min=0, max=0.02, value=0.1, id='tab-3-slider-K2',
                        tooltip={"placement": "bottom", "always_visible": True},
                    )], width=10),
                ]),
                html.Br(),
                dbc.Row([dbc.Button(["Aplicar"], id='tab-3-apply-button')]),
                html.Br(),
            ], width=3),
            dbc.Col([
                html.Center([html.H3(["Dados experimentais"])]),
                html.Br(),
                dbc.Row([
                    #dbc.Col(["Dados:"], width=1),
                    dbc.Col([
                        dcc.Dropdown(
                            options=data_dropdown_options,
                            value = data_start_option,
                            clearable = False,
                            id='tab-3-dropdown-data'
                        ),
                    ]),
                ]),
                dcc.Graph(id='tab-3-grafico',
                          figure=fig),
            ])
        ]),
        html.H3(["Regressão não linear"]),
        html.Br(),
        dbc.Row([
            dbc.Col([dcc.Markdown("$C_1$", id='tab-3-regression-data-C1', mathjax=True),
                        dcc.Markdown("$C_2$", id='tab-3-regression-data-C2', mathjax=True),
                     ]),
            dbc.Col([dcc.Markdown("$K_1$", id='tab-3-regression-data-K1', mathjax=True),
                        dcc.Markdown("$K_2$", id='tab-3-regression-data-K2', mathjax=True),
                     ]),
        ]),
    ]

    return tab

def update_graph_data(exp_data, new_data, const, figure):
    t, r = exp_data[new_data]['t'], exp_data[new_data]['r']
    ut, ur = exp_data[new_data]['ut'], exp_data[new_data]['ur']

    figure['layout']['title'] = f'Distância vs Tempo - {new_data}'

    figure['data'][0]['x'] = t
    figure['data'][0]['y'] = r
    figure['data'][0]['error_x']['array'] = ut
    figure['data'][0]['error_y']['array'] = ur

    # Linear regression
    # ===
    C1, C2, K1, K2 = const[0], const[1], const[2], const[3]

    d = lambda t : K1 * np.exp(-C2*(t)) + (C1*C2*(t) - C1)/(C2**2) + K2

    linspace = np.linspace(t[0], t[-1], 250)

    figure['data'][1]['x'] = linspace
    figure['data'][1]['y'] = d(linspace)

    return figure

# Callbacks
# ===

@callback(
    Output('tab-3-grafico', 'figure'),
    Input('tab-3-dropdown-data', 'value'),
    Input('tab-3-slider-C1', 'value'),
    Input('tab-3-slider-C2', 'value'),
    Input('tab-3-slider-K1', 'value'),
    Input('tab-3-slider-K2', 'value'),
    State('tab-3-grafico', 'figure'),
)
def update_output(data_value, C1, C2, K1, K2, figure):
    return update_graph_data(generate_tab.exp_data, data_value, [C1, C2, K1, K2], figure)
