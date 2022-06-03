# Configuração do Dash
import plotly.graph_objects as go # biblioteca plotly, para plots interativos
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, ctx
from dash import Input, Output, State, callback

from model import *

import numpy as np

# Tab-2
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
            mode="lines",
            visible=True,
            line=dict(color="#8fa3e8", width=3),
        )
    )

    dropdown_options = list(measure_data['experimental-data'].keys())
    start_option = config['test-model-tab']['start_option']
    update_graph_data(exp_data, start_option, fig,
                      config['test-model-tab']['value_A'],
                      config['test-model-tab']['value_B'])

    tab_2 = [
        dcc.Dropdown(
            options=dropdown_options,
            value = start_option,
            clearable = False,
            id='tab-2-dropdown-dados'
        ),
        dcc.Graph(id='tab-2-grafico',
                  figure=fig),
        dbc.Row([
            dbc.Col(children=[dcc.Slider(min=-2, max=2, value=0.5, id='tab-2-sliderA',
                                         tooltip={"placement": "bottom", "always_visible": True})
                              ], width=10),
            dbc.Col(children=["Slider A"]),
        ]),
        dbc.Row([
            dbc.Col([dcc.Slider(
                min=-2, max=2, value=0.5, id='tab-2-sliderB',
                tooltip={"placement": "bottom", "always_visible": True},
            )], width=10),
            dbc.Col(children=["Slider B"]),
        ]),
        dbc.Row([
            dbc.Col([dcc.Slider(
                min=-2, max=2, value=1, id='tab-2-sliderTau',
                tooltip={"placement": "bottom", "always_visible": True},
            )], width=10),
            dbc.Col(children=["Slider τ"]),
        ]),
    ]

    return tab_2

def update_graph_data(exp_data, new_data, figure, A, B):
    t, r = exp_data[new_data]['t'], exp_data[new_data]['r']
    ut, ur = exp_data[new_data]['ut'], exp_data[new_data]['ur']
    r0, tc = exp_data[new_data]['r0'], exp_data[new_data]['tc']
    t0 = exp_data[new_data]['t0']
    tau, utau = non_linear_regression(exp_data[new_data], A, B)

    figure['layout']['title'] = f'Distância vs Tempo - {new_data}'

    figure['data'][0]['x'] = t
    figure['data'][0]['y'] = r
    figure['data'][0]['error_x']['array'] = ut
    figure['data'][0]['error_y']['array'] = ur

    linspace = np.linspace(t0, tc, 250)
    f = lambda A, B, t : A * np.exp(-t) + B * np.exp(t)
    r = lambda t : (r0/(f(A,B,tc/tau) - 1))*(f(A,B,tc/tau) - f(A,B,t/tau))

    figure['data'][1]['x'] = linspace
    figure['data'][1]['y'] = r(linspace)
    figure['data'][1]['name'] =f"Modelo com τ = {tau:.2f} +/- {utau:.2f}"

    return figure

def update_graph_function(current_data, figure, A, B, new_tau = None):
    r0, tc = current_data['r0'], current_data['tc']

    if new_tau == None:
        tau, utau = non_linear_regression(current_data, A, B)
        figure['data'][1]['name'] = f"Modelo com τ = {tau:.2f} +/- {utau:.2f}"
    else:
        tau = np.float64(new_tau)
        figure['data'][1]['name'] = f"Modelo com τ = {tau:.2f}"

    f = lambda A, B, t : A * np.exp(-t) + B * np.exp(t)
    r = lambda t : (r0/(f(A,B,tc/tau) - 1))*(f(A,B,tc/tau) - f(A,B,t/tau))
    figure['data'][1]['y'] = r(figure['data'][1]['x'])

    return figure

@callback(
    Output('tab-2-grafico', 'figure'),
    Input('tab-2-dropdown-dados', 'value'),
    Input('tab-2-sliderA', 'value'),
    Input('tab-2-sliderB', 'value'),
    Input('tab-2-sliderTau', 'value'),
    State('tab-2-grafico', 'figure'))
def update_output(dropdown, valueA, valueB, valueTau, figure):
    current_data = generate_tab.exp_data[dropdown]
    if ctx.triggered_id == 'tab-2-dropdown-dados':
        return update_graph_data(generate_tab.exp_data, dropdown,
                                 figure, valueA, valueB)
    elif ctx.triggered_id == 'tab-2-sliderTau':
        return update_graph_function(current_data, figure,
                                     valueA, valueB, valueTau)
    else:
        return update_graph_function(current_data, figure,
                                     valueA, valueB)
