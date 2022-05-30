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
            name="Regressão linear",
            mode="lines",
            visible=True,
            line=dict(color="#8fa3e8", width=3),
        )
    )

    data_dropdown_options = list(measure_data['experimental-data'].keys())
    data_start_option = config['test-model-tab']['start_option']

    x_axis_options = ['Tempo',
                      'Log(Tempo)',
                      'Exp(Tempo)']
    x_axis_start_option = 'Tempo'

    y_axis_options = ['Distância',
                      'Log(Distância)',
                      'Exp(Distância)']
    y_axis_start_option = 'Distância'

    tab_1 = [
        dbc.Row([
            dbc.Col([
                html.H3(["Opções"]),
                html.Br(),
                dbc.Row([
                    dbc.Col(["Dados:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=data_dropdown_options,
                            value = data_start_option,
                            clearable = False,
                            id='tab-1-dropdown-data'
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(["Eixo x:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=x_axis_options,
                            value = x_axis_start_option,
                            clearable = False,
                            id='tab-1-dropdown-x-axis'
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(["Eixo y:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=y_axis_options,
                            value = y_axis_start_option,
                            clearable = False,
                            id='tab-1-dropdown-y-axis'
                        ),
                    ]),
                ]),
                html.Br(),
                dbc.Row([dbc.Button(["Aplicar"], id='tab-1-apply-button')]),
            ], width=3),
            dbc.Col([
                html.Center([html.H3(["Dados experimentais"])]),
                dcc.Graph(id='tab-1-grafico',
                          figure=fig),
            ])
        ]),
    ]

    #update_graph_data(exp_data, data_start_option,
    #                  x_axis_start_option, y_axis_start_option, fig)

    return tab_1

def update_graph_data(exp_data, new_data, x_axis, y_axis, figure):
    t, r = exp_data[new_data]['t'], exp_data[new_data]['r']
    ut, ur = exp_data[new_data]['ut'], exp_data[new_data]['ur']

    figure['layout']['title'] = f'{x_axis} vs {y_axis} - {new_data}'
    #print(figure['layout']['xaxis']['title']['text'])
    figure['layout']['xaxis']['title']['text'] = x_axis
    figure['layout']['yaxis']['title']['text'] = y_axis

    if x_axis == 'Tempo':
        figure['layout']['xaxis']['title']['text'] = 'Tempo (s)'
    elif x_axis == 'Log(Tempo)':
        x = unumpy.uarray(t, ut)
        x = unumpy.log(x)
        t, ut = unumpy.nominal_values(x), unumpy.std_devs(x)
    elif x_axis == 'Exp(Tempo)':
        x = unumpy.uarray(t, ut)
        x = unumpy.exp(x)
        t, ut = unumpy.nominal_values(x), unumpy.std_devs(x)

    if y_axis == 'Distância':
        figure['layout']['yaxis']['title']['text'] = 'Distância (m)'
    elif y_axis == 'Log(Distância)':
        y = unumpy.uarray(r, ur)
        y = unumpy.log(y)
        r, ur = unumpy.nominal_values(y), unumpy.std_devs(y)
    elif y_axis == 'Exp(Distância)':
        y = unumpy.uarray(r, ur)
        y = unumpy.exp(y)
        r, ur = unumpy.nominal_values(y), unumpy.std_devs(y)

    figure['data'][0]['x'] = t
    figure['data'][0]['y'] = r
    figure['data'][0]['error_x']['array'] = ut
    figure['data'][0]['error_y']['array'] = ur

    # linspace = np.linspace(t0, tc, 250)
    # f = lambda A, B, t : A * np.exp(-t) + B * np.exp(t)
    # r = lambda t : (r0/(f(A,B,tc/tau) - 1))*(f(A,B,tc/tau) - f(A,B,t/tau))

    # figure['data'][1]['x'] = linspace
    # figure['data'][1]['y'] = r(linspace)
    # figure['data'][1]['name'] =f"Modelo com τ = {tau:.2f} +/- {utau:.2f}"

    return figure

# Callbacks
# ===

@callback(
    Output('tab-1-grafico', 'figure'),
    [Input('tab-1-apply-button', 'n_clicks')],
    State('tab-1-dropdown-data', 'value'),
    State('tab-1-dropdown-x-axis', 'value'),
    State('tab-1-dropdown-y-axis', 'value'),
    State('tab-1-grafico', 'figure'),
)
def on_button_click(button_value, data_value, x_value, y_value, figure):
    return update_graph_data(generate_tab.exp_data, data_value, x_value, y_value, figure)
