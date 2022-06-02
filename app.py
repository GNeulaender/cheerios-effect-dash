#
# Bibliotecas e configurações gerais
#
import numpy as np #numpy: array n-dimensionais
from scipy import odr #odr: "Orthogonal distance regression", usada para o MMQ
import pandas as pd #pandas: importar dados em .csv e .xlsx
import math #math: funções matemáticas do python

# biblioteca de propagação de incertezas
from uncertainties import ufloat #ufloat: variaveis float + incerteza
from uncertainties import umath
from uncertainties.umath import * # importa funções matemáticas que trabalham com
                                  # as incertezas do ufloat
from aux_func import * # importa funções auxiliares
from model import * # importa funções auxiliares

#
# Configurações
#
import yaml
from yaml import Loader

config_file = open('config.yaml', 'r')
config = yaml.load(config_file, Loader=Loader)

measure_data_file = open(config['general']['measure-data-file'], 'r')
measure_data = yaml.load(measure_data_file, Loader=Loader)

#
# Importa dados e faz correções
#

exp_data = import_exp_data(config['general']['video-data-file'],
                           measure_data['experimental-data'].keys())

# Regressão não-linear

for name in exp_data.keys():
    tau, utau = non_linear_regression(exp_data[name],
                                      config['test-model-tab']['value_A'],
                                      config['test-model-tab']['value_B'])
    exp_data[name]['tau'] = tau
    exp_data[name]['utau'] = utau

#
# Gráfico interativo
#

# Funções
def f(A,B,x):
  return A*np.exp(-x) + B*np.exp(x)

def r(T,t,r0,tc,A,B):
  return (r0/(f(A,B,tc/T) - 1))*(f(A,B,tc/T) - f(A,B,t/T))

def change_data(new_data, figure, A, B):
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
    r = lambda t : (r0/(f(A,B,tc/tau) - 1))*(f(A,B,tc/tau) - f(A,B,t/tau))

    figure['data'][1]['x'] = linspace
    figure['data'][1]['y'] = r(linspace)
    figure['data'][1]['name'] =f"Modelo com τ = {tau:.2f} +/- {utau:.2f}"

# Configuração do Dash
import plotly.graph_objects as go # biblioteca plotly, para plots interativos
from dash import Dash, html, dcc, ctx
from dash import Input, Output, State
import dash_bootstrap_components as dbc
import dash_defer_js_import as dji

import tab_1, tab_3

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',
#                        'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/styles/monokai-sublime.min.css']

external_stylesheets = [dbc.themes.BOOTSTRAP]
# external_scripts=["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML" ]

dash_app = Dash(__name__,
                #meta_tags=[{"content": "width=device-width, initial-scale=1"}],
                external_stylesheets=external_stylesheets)
app = dash_app.server

# Tab-2
# ===

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

tab_2 = [
    dcc.Dropdown(
        options=dropdown_options,
        value = start_option,
        clearable = False,
        id='dropdown-dados'
    ),
    dcc.Graph(id='grafico',
              figure=fig),
    dbc.Row([
    dbc.Col(children=[dcc.Slider(min=-2, max=2, value=0.5, id='sliderA',
        tooltip={"placement": "bottom", "always_visible": True})
        ], width=10),
    dbc.Col(children=["Slider A"]),
    ]),
    dbc.Row([
    dbc.Col([dcc.Slider(
        min=-2, max=2, value=0.5, id='sliderB',
        tooltip={"placement": "bottom", "always_visible": True},
        )], width=10),
    dbc.Col(children=["Slider B"]),
    ]),
]

# App layout
# ===

tab_1 = tab_1.generate_tab(config, measure_data, exp_data)
tab_3 = tab_3.generate_tab(config, measure_data, exp_data)

dash_app.layout = html.Div([
    dbc.Container(children=[
        html.H1(children=["Grafico interativo"]),
        dcc.Markdown('$\\LaTeX$', mathjax=True),
        html.Br(),
        dcc.Tabs(id='tabs-component', value='tab-3', children=[
            dcc.Tab(label='Dados experimentais', value='tab-1'),
            dcc.Tab(label='Modelo 1', value='tab-2'),
            dcc.Tab(label='Modelo 2', value='tab-3'),
        ]),
        html.Br(),
        dbc.Container(id='tabs-content', fluid=True),
    ]),
])

@dash_app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-component', 'value')
)
def update_output(value):
    if value == 'tab-1':
        return tab_1
    elif value == 'tab-2':
        A, B = config['test-model-tab']['value_A'], config['test-model-tab']['value_B']
        change_data(start_option, fig, A, B)
        return tab_2
    elif value == 'tab-3':
        return tab_3


@dash_app.callback(
    Output('grafico', 'figure'),
    Input('dropdown-dados', 'value'),
    Input('sliderA', 'value'),
    Input('sliderB', 'value'),
    State('grafico', 'figure'))
def update_output(dropdown, valueA, valueB, figure):
    if ctx.triggered_id == 'dropdown-dados':
        change_data(dropdown, figure, valueA, valueB)
    else:
        A, B = valueA, valueB
        r0, tc = exp_data[dropdown]['r0'], exp_data[dropdown]['tc']
        tau, utau =  non_linear_regression(exp_data[dropdown], A, B)
        r = lambda t : (r0/(f(A,B,tc/tau) - 1))*(f(A,B,tc/tau) - f(A,B,t/tau))
        figure['data'][1]['y'] = r(figure['data'][1]['x'])
        figure['data'][1]['name'] =f"Modelo com τ = {tau:.2f} +/- {utau:.2f}"
    return figure

if __name__ == '__main__':
    dash_app.run_server(debug=True)
