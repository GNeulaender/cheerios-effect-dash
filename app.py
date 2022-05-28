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

#
# Importa dados e faz correções
#

exp_data = dict()
sheet_names = ["Profundidade 1",
               "Profundidade 2",
               "Profundidade 3"
               ]

# Incertezas
utempo = uretangular(1/60)
uprof = utriangular(2*(24.3E-3 - 23.1E-3)) # incerteza da profundidade (metros)
uregua = utriangular(1E-2)
upos = uregua # incerteza da posição da tarraxinha

d_correction = 1.044097747E-2

# Dados
for sheet in sheet_names:
    raw_data = pd.read_excel('dados-videos.xlsx',
                             sheet_name=sheet)
    t, r = np.array(raw_data['t']), np.array(raw_data['L']) - d_correction
    ut, ur = np.array([utempo for i in t]), np.array([upos for i in r])
    exp_data[sheet] = {
        't' : t, # dados do tempo
        'ut' : ut, # incerteza do tempo
        'r' : r, # dados da distância
        'ur' : ur, # incerteza da distância
        'r0' : r[0], # distância inicial
        't0' : t[0], # distância inicial
        'tc' : t[-1] + 1/60 # tempo de contato
    }


# Regressão não-linear

for name in exp_data.keys():
    t, r = exp_data[name]['t'], exp_data[name]['r']
    ut, ur = exp_data[name]['ut'], exp_data[name]['ur']
    r0, tc = exp_data[name]['r0'], exp_data[name]['tc']

    def f(T, t):
        '''Função não linear r = r(t)'''
        return (r0/(np.cosh(tc/T[0]) - 1))*(np.cosh(tc/T[0]) - np.cosh(t/T[0]))

    modelo = odr.Model(f)

    mydata = odr.RealData(t, r, sx=ut, sy=ur)
    myodr = odr.ODR(mydata, modelo, beta0=[1.])
    myoutput = myodr.run()

    tau = myoutput.beta[0]
    utau = myoutput.sd_beta[0]

    exp_data[name]['tau'] = tau
    exp_data[name]['utau'] = utau

#
# Gráfico interativo
#

# Funções
def f(A,B,x):
  return A*np.e**(-x) + B*np.e**x

def r(T,t,r0,tc,A,B):
  return (r0/(f(A,B,tc/T) - 1))*(f(A,B,tc/T) - f(A,B,t/T))

def change_data(new_data, figure):
    t, r = exp_data[new_data]['t'], exp_data[new_data]['r']
    ut, ur = exp_data[new_data]['ut'], exp_data[new_data]['ur']
    r0, tc = exp_data[new_data]['r0'], exp_data[new_data]['tc']
    t0 = exp_data[new_data]['t0']
    tau, utau = exp_data[new_data]['tau'], exp_data[new_data]['utau']

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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = Dash(__name__, external_stylesheets=external_stylesheets)
app = dash_app.server

fig = go.Figure()

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

A,B = 0.5,0.5
fig.add_trace(
    go.Scatter(
        mode="lines",
        visible=True,
        line=dict(color="#8fa3e8", width=3),
    )
)

start_option = 'Profundidade 2'
change_data(start_option, fig)

dash_app.layout = html.Div(children=[
    html.H1(children=["Grafico interativo"]),
    #html.P(children=["Paragrafo com informações"]),
    dcc.Dropdown(
        options=sheet_names,
        value = start_option,
        clearable = False,
        id='dropdown-dados'
    ),
    dcc.Graph(id='grafico',
              figure=fig),
    html.Label("Slider A"),
    dcc.Slider(
        min=0,
        max=5,
        step=0.1,
        value=0.5,
        id='sliderA'
    ),
    html.Label("Slider B"),
    dcc.Slider(
        min=0,
        max=5,
        step=0.1,
        value=0.5,
        id='sliderB'
    )
])

@dash_app.callback(
    Output('grafico', 'figure'),
    Input('dropdown-dados', 'value'),
    Input('sliderA', 'value'),
    Input('sliderB', 'value'),
    State('grafico', 'figure'))
def update_output(dropdown, valueA, valueB, figure):
    if ctx.triggered_id == 'dropdown-dados':
        change_data(dropdown, figure)
    else:
        A, B = valueA, valueB
        r0, tc, tau = exp_data[dropdown]['r0'], exp_data[dropdown]['tc'], exp_data[dropdown]['tau']
        r = lambda t : (r0/(f(A,B,tc/tau) - 1))*(f(A,B,tc/tau) - f(A,B,t/tau))
        figure['data'][1]['y'] = r(figure['data'][1]['x'])
    return figure

if __name__ == '__main__':
    dash_app.run_server(debug=True)
