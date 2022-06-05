# Configuração do Dash
import plotly.graph_objects as go # biblioteca plotly, para plots interativos
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, ctx, dash_table
from dash import Input, Output, State, callback

from model import *

import numpy as np
from uncertainties import unumpy
from uncertainties.umath import *

def generate_tab(config, measure_data, exp_data):
    generate_tab.exp_data = exp_data
    generate_tab.measure_data = measure_data

    fig_C1 = go.Figure(
        {'layout' : {
            'xaxis_title' : 'Profundidade',
            'yaxis_title' : 'C1',
            'legend_title' : 'Legenda',
        }}
    )

    fig_C2 = go.Figure(
        {'layout' : {
            'xaxis_title' : 'Profundidade',
            'yaxis_title' : 'C2',
            'legend_title' : 'Legenda',
        }}
    )

    trace_data = go.Scatter(
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

    trace_line = go.Scatter(
        name="Regressão linear",
        mode="lines",
        visible=True,
        line=dict(color="#8fa3e8", width=3),
    )

    fig_C1.add_trace(trace_data), fig_C1.add_trace(trace_line)
    fig_C2.add_trace(trace_data), fig_C2.add_trace(trace_line)

    tags_options = ['Lantejoulas', 'Profundidade', 'Alcool']
    starting_tag = 'Profundidade'
    y_axis_options_C1 = ['C1', 'Log(C1)']
    y_axis_options_C2 = ['-C2', 'Log(-C2)']
    starting_y_axis_C1 = 'C1'
    starting_y_axis_C2 = '-C2'

    x_axis_options = []
    starting_x_axis = starting_tag

    tab_4 = [
        # Página do C1
        # ===
        dbc.Row([
            dbc.Col([
                html.H3(["Opções C1"]),
                html.Br(),
                dbc.Row([
                    dbc.Col(["Dados:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=tags_options,
                            value = starting_tag,
                            clearable = False,
                            id='tab-4-tags-C1'
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(["Eixo x:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=x_axis_options,
                            value = starting_x_axis,
                            clearable = False,
                            id='tab-4-x-axis-C1'
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(["Eixo y:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=y_axis_options_C1,
                            value = starting_y_axis_C1,
                            clearable = False,
                            id='tab-4-y-axis-C1'
                        ),
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Markdown(r"#### Regressão linear ($y = Ax + B$):", mathjax=True),
                             dcc.Markdown("A", id='tab-4-regression-A-C1', mathjax=True),
                             dcc.Markdown("B", id='tab-4-regression-B-C1', mathjax=True),
                             ])
                ]),
                html.Br(),
                dbc.Row([dbc.Button(["Aplicar"], id='tab-4-apply-button-C1')]),
            ], width=3),
            dbc.Col([
                html.Center([html.H3(["Dados experimentais"])]),
                dcc.Graph(id='tab-4-graph-C1',
                          figure=fig_C1),
            ])
        ]),
        dbc.Accordion([
            dbc.AccordionItem([
                dash_table.DataTable(id='tab-4-table-C1')
            ], title="Tabela de Dados do C1"),
        ],start_collapsed=True),

        html.Br(), # Espaçamento
        # Página do C2
        # ===
        dbc.Row([
            dbc.Col([
                html.H3(["Opções C2"]),
                html.Br(),
                dbc.Row([
                    dbc.Col(["Dados:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=tags_options,
                            value = starting_tag,
                            clearable = False,
                            id='tab-4-tags-C2'
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(["Eixo x:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=x_axis_options,
                            value = starting_x_axis,
                            clearable = False,
                            id='tab-4-x-axis-C2'
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(["Eixo y:"], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            options=y_axis_options_C2,
                            value = starting_y_axis_C2,
                            clearable = False,
                            id='tab-4-y-axis-C2'
                        ),
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Markdown(r"#### Regressão linear ($y = Ax + B$):", mathjax=True),
                             dcc.Markdown("A", id='tab-4-regression-A-C2', mathjax=True),
                             dcc.Markdown("B", id='tab-4-regression-B-C2', mathjax=True),
                             ])
                ]),
                html.Br(),
                dbc.Row([dbc.Button(["Aplicar"], id='tab-4-apply-button-C2')]),
            ], width=3),
            dbc.Col([
                html.Center([html.H3(["Dados experimentais"])]),
                dcc.Graph(id='tab-4-graph-C2',
                          figure=fig_C2),
            ])
        ]),
        dbc.Accordion([
            dbc.AccordionItem([
                dash_table.DataTable(id='tab-4-table-C2')
            ], title="Tabela de Dados do C2"),
        ],start_collapsed=True),
    ]

    return tab_4

def update_graph_data(exp_data, measure_data, new_tag, x_axis, y_axis, figure):
    x, ux, y, uy = [], [], [], []
    measure_data = measure_data['experimental-data']

    data_name = 'C1 (m/s^2)'
    if 'C2' in y_axis:
        data_name = 'C2 (1/s)'
    tag_name = ''

    for name in exp_data.keys():
        if not(new_tag.lower() in name.lower()):
            continue

        if new_tag == 'Lantejoulas':
            tag_name = 'Massa (kg)'
            x.append(measure_data[name]['massa'])
            ux.append(measure_data[name]['umassa'])
        elif new_tag == 'Profundidade':
            tag_name = 'Profundidade (m)'
            x.append(measure_data[name]['profundidade'])
            ux.append(measure_data[name]['uprofundidade'])
        elif new_tag == 'Alcool':
            tag_name = 'Concentração'
            x.append(measure_data[name]['concentracao'])
            ux.append(measure_data[name]['uconcentracao'])

        C1, uC1, C2, uC2 = non_linear_model(exp_data[name], [0.01, -1])
        if 'C1' in data_name:
            y.append(C1), uy.append(uC1)
        else:
            y.append(-C2), uy.append(uC2)

    x, ux = np.array(x), np.array(ux)
    y, uy = np.array(y), np.array(uy)

    # Table data
    # ===
    table_data = pd.DataFrame({
        f'{data_name}' :  y,
        f'u{data_name}' :uy,
        f'{tag_name}' :  x,
        f'u{tag_name}' : ux,
    })

    figure['layout']['title'] = f'{x_axis} vs {y_axis}'

    figure['layout']['xaxis']['title']['text'] = x_axis
    figure['layout']['yaxis']['title']['text'] = y_axis

    if x_axis in ['Log(Lantejoulas)', 'Log(Profundidade)', 'Log(Alcool)']:
        filter_array = [(i > 0) for i in x]
        x_ = unumpy.uarray(x[filter_array], ux[filter_array])
        x_ = unumpy.log(x_)
        x, ux = unumpy.nominal_values(x_), unumpy.std_devs(x_)
        y, uy = y[filter_array], uy[filter_array]

    if y_axis in ['Log(C1)', 'Log(-C2)']:
        filter_array = [(i > 0) for i in y]
        y_ = unumpy.uarray(y[filter_array], uy[filter_array])
        y_ = unumpy.log(y_)
        y, uy = unumpy.nominal_values(y_), unumpy.std_devs(y_)
        x, ux = x[filter_array], ux[filter_array]

    figure['data'][0]['x'] = x
    figure['data'][0]['y'] = y
    figure['data'][0]['error_x']['array'] = ux
    figure['data'][0]['error_y']['array'] = uy

    # Linear regression
    # ===

    A, uA, B, uB = linear_regression(x, ux, y, uy)

    line = lambda x : A*x + B

    linspace = np.linspace(x[0], x[-1], 250)

    figure['data'][1]['x'] = linspace
    figure['data'][1]['y'] = line(linspace)

    A_text = f"A = {A:.4f} $\\pm$ {uA:.4f}"
    B_text = f"B = {B:.4f} $\\pm$ {uB:.4f}"

    return figure, A_text, B_text, table_data

@callback(
    Output('tab-4-x-axis-C1', 'options'),
    Output('tab-4-x-axis-C1', 'value'),
    Input('tab-4-tags-C1', 'value'),
)
def update_options(current_tag):
    return [current_tag, f'Log({current_tag})'], current_tag

@callback(
    Output('tab-4-graph-C1', 'figure'),
    Output('tab-4-regression-A-C1', 'children'),
    Output('tab-4-regression-B-C1', 'children'),
    Output('tab-4-table-C1', 'data'),
    Output('tab-4-table-C1', 'columns'),
    [Input('tab-4-apply-button-C1', 'n_clicks')],
    State('tab-4-tags-C1', 'value'),
    State('tab-4-x-axis-C1', 'value'),
    State('tab-4-y-axis-C1', 'value'),
    State('tab-4-graph-C1', 'figure'),
)
def on_button_click(button_value, current_tag, x_axis, y_axis, figure):
    new_fig, textA, textB, new_data = update_graph_data(generate_tab.exp_data, generate_tab.measure_data, current_tag, x_axis, y_axis, figure)
    data_dict = new_data.to_dict('records')
    data_columns = [{"name" : i, "id" : i} for i in new_data.columns]
    return new_fig, textA, textB, data_dict, data_columns

@callback(
    Output('tab-4-x-axis-C2', 'options'),
    Output('tab-4-x-axis-C2', 'value'),
    Input('tab-4-tags-C2', 'value'),
)
def update_options(current_tag):
    return [current_tag, f'Log({current_tag})'], current_tag

@callback(
    Output('tab-4-graph-C2', 'figure'),
    Output('tab-4-regression-A-C2', 'children'),
    Output('tab-4-regression-B-C2', 'children'),
    Output('tab-4-table-C2', 'data'),
    Output('tab-4-table-C2', 'columns'),
    [Input('tab-4-apply-button-C2', 'n_clicks')],
    State('tab-4-tags-C2', 'value'),
    State('tab-4-x-axis-C2', 'value'),
    State('tab-4-y-axis-C2', 'value'),
    State('tab-4-graph-C2', 'figure'),
)
def on_button_click(button_value, current_tag, x_axis, y_axis, figure):
    new_fig, textA, textB, new_data = update_graph_data(generate_tab.exp_data, generate_tab.measure_data, current_tag, x_axis, y_axis, figure)
    data_dict = new_data.to_dict('records')
    data_columns = [{"name" : i, "id" : i} for i in new_data.columns]
    return new_fig, textA, textB, data_dict, data_columns
