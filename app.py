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

# for name in exp_data.keys():
#     tau, utau = non_linear_regression(exp_data[name],
#                                       config['test-model-tab']['value_A'],
#                                       config['test-model-tab']['value_B'])
#     exp_data[name]['tau'] = tau
#     exp_data[name]['utau'] = utau

#
# Gráfico interativo
#

# Configuração do Dash
import plotly.graph_objects as go # biblioteca plotly, para plots interativos
from dash import Dash, html, dcc, ctx
from dash import Input, Output, State
import dash_bootstrap_components as dbc
import dash_defer_js_import as dji

import tab_1, tab_3, tab_4

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',
#                        'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/styles/monokai-sublime.min.css']

external_stylesheets = [dbc.themes.BOOTSTRAP]
# external_scripts=["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML" ]

dash_app = Dash(__name__,
                #meta_tags=[{"content": "width=device-width, initial-scale=1"}],
                suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets)
app = dash_app.server

# App layout
# ===

tab_1 = tab_1.generate_tab(config, measure_data, exp_data)
# tab_2 = tab_2.generate_tab(config, measure_data, exp_data)
tab_3 = tab_3.generate_tab(config, measure_data, exp_data)
tab_4 = tab_4.generate_tab(config, measure_data, exp_data)

dash_app.layout = html.Div([
    dbc.Container(children=[
        html.H1(children=["Grafico interativo"]),
        dcc.Markdown('$\\LaTeX$', mathjax=True),
        html.Br(),
        dcc.Tabs(id='tabs-component', value='tab-4', children=[
            dcc.Tab(label='Dados experimentais', value='tab-1'),
            # dcc.Tab(label='Modelo 1', value='tab-2'),
            dcc.Tab(label='Modelo', value='tab-3'),
            dcc.Tab(label='Resultados', value='tab-4'),
        ]),
        html.Br(),
        dbc.Container(id='tabs-content', fluid=True),
    ], fluid=True),
])

@dash_app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-component', 'value')
)
def update_output(value):
    if value == 'tab-1':
        return tab_1
    # elif value == 'tab-2':
    #     return tab_2
    elif value == 'tab-3':
        return tab_3
    elif value == 'tab-4':
        return tab_4

if __name__ == '__main__':
    dash_app.run_server(debug=True)
