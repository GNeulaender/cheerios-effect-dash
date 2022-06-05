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
            line=dict(color="#e60000", width=3),
        )
    )

    data_dropdown_options = list(measure_data['experimental-data'].keys())
    data_start_option = config['test-model-tab']['start_option']


    tab = [
        dbc.Accordion([
            dbc.AccordionItem([
                "Aqui será colocado um arquivo Markdown"
            ], title="Mais informações"),
        ],start_collapsed=True),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H3(["Opções"]),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Markdown('$C_1$:', mathjax=True)], width=2),
                    dbc.Col([dcc.Slider(
                        min=0, max=0.01, value=0.001, id='tab-3-slider-C1',
                        tooltip={"placement": "bottom", "always_visible": True},
                    )]),
                ]),
                dbc.Row([
                    dbc.Col([dcc.Markdown('$C_2$:', mathjax=True)], width=2),
                    dbc.Col([dcc.Slider(
                        min=-5, max=0, value=-1, id='tab-3-slider-C2',
                        tooltip={"placement": "bottom", "always_visible": True},
                    )]),
                ]),
                html.Br(),
                dbc.Row([dbc.Button(["Aplicar"], id='tab-3-apply-button')]),
                html.Br(),
                html.H3(["Regressão não linear"]),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Markdown("$C_1$", id='tab-3-regression-data-C1', mathjax=True),
                             dcc.Markdown("$C_2$", id='tab-3-regression-data-C2', mathjax=True),
                             ]),
                ]),
            ], width=3),
            dbc.Col([
                html.Center([html.H3(["Dados experimentais"])]),
                html.Br(),
                dcc.Dropdown(
                    options=data_dropdown_options,
                    value = data_start_option,
                    clearable = False,
                    id='tab-3-dropdown-data'
                ),
                dcc.Graph(id='tab-3-grafico',
                          figure=fig, config={'edits': {'legendPosition' : True,
                                                        'legendText' : True}}),
            ])
        ]),
    ]

    return tab

def update_graph_data(exp_data, new_data, const, figure):
    t, r = exp_data[new_data]['t'], exp_data[new_data]['r']
    ut, ur = exp_data[new_data]['ut'], exp_data[new_data]['ur']
    tc, r0 = exp_data[new_data]['tc'], exp_data[new_data]['r0']

    figure['layout']['title'] = f'Distância vs Tempo - {new_data}'

    figure['data'][0]['x'] = t
    figure['data'][0]['y'] = r
    figure['data'][0]['error_x']['array'] = ut
    figure['data'][0]['error_y']['array'] = ur

    figure = update_graph_function(exp_data[new_data], const, figure)

    return figure

def update_graph_function(current_data, const, figure):
    tc, r0 = current_data['tc'], current_data['r0']

    C1, C2 = const[0], const[1]

    d = lambda t : (((C1/C2)*tc + r0)/(1 - np.exp(-C2*tc)))*(np.exp(-C2*t) - 1) + (C1/C2)*t + r0

    linspace = np.linspace(figure['data'][0]['x'][0], tc, 250)

    figure['data'][1]['x'] = linspace
    figure['data'][1]['y'] = d(linspace)

    return figure

def update_regression(current_data, const, figure):
    tc, r0 = current_data['tc'], current_data['r0']
    C1, uC1, C2, uC2 = non_linear_model(current_data, const)

    d = lambda t : (((C1/C2)*tc + r0)/(1 - np.exp(-C2*tc)))*(np.exp(-C2*t) - 1) + (C1/C2)*t + r0

    linspace = np.linspace(figure['data'][0]['x'][0], tc, 250)

    figure['data'][2]['x'] = linspace
    figure['data'][2]['y'] = d(linspace)

    textC1 = f'$C_1 = {C1:.4f} \\pm {uC1:.4f}$'
    textC2 = f'$C_2 = {C2:.4f} \\pm {uC2:.4f}$'

    return figure, textC1, textC2

# Callbacks
# ===

@callback(
    Output('tab-3-grafico', 'figure'),
    Output('tab-3-regression-data-C1', 'children'),
    Output('tab-3-regression-data-C2', 'children'),
    [Input('tab-3-apply-button', 'n_clicks'),
    Input('tab-3-dropdown-data', 'value'),
    Input('tab-3-slider-C1', 'value'),
    Input('tab-3-slider-C2', 'value')],
    State('tab-3-grafico', 'figure'),
    State('tab-3-regression-data-C1', 'children'),
    State('tab-3-regression-data-C2', 'children'),
)
def update_output(n_clicks, data_value, C1, C2, figure, textC1, textC2):
    current_data = generate_tab.exp_data[data_value]
    if ctx.triggered_id == 'tab-3-apply-button':
        return update_regression(current_data, [C1, C2], figure)
    elif (ctx.triggered_id == 'tab-3-dropdown-data') or (ctx.triggered_id == None):
        new_fig = update_graph_data(generate_tab.exp_data, data_value, [C1, C2], figure)
        return new_fig, textC1, textC2
    else:
        new_fig = update_graph_function(current_data, [C1, C2], figure)
        return new_fig, textC1, textC2
