import numpy as np
from scipy import odr
import pandas as pd
import yaml
from yaml import Loader

import uncertainties
from uncertainties import ufloat
from uncertainties import unumpy
from uncertainties.umath import *

config_file = open('config.yaml', 'r')
config = yaml.load(config_file, Loader=Loader)['general']

data_config_file = open(config['measure-data-file'], 'r')
data_config = yaml.load(data_config_file, Loader=Loader)['general']

def import_exp_data(xlsx_file, sheet_list) -> dict:
    exp_data = dict()

    upos = data_config['uposicao-tracker']
    utempo = data_config['utempo-tracker']
    r_correction = ufloat(data_config['diametro-tarraxinha'],
                          data_config['udiametro-tarraxinha'])

    for sheet in sheet_list:
        raw_data = pd.read_excel(xlsx_file, sheet_name=sheet)

        t = unumpy.uarray(raw_data['t'], utempo)
        r = unumpy.uarray(raw_data['L'], upos) - r_correction
        exp_data[sheet] = {
            't' : unumpy.nominal_values(t), # dados do tempo
            'ut' : unumpy.std_devs(t), # incerteza do tempo
            'r' : unumpy.nominal_values(r), # dados da distância
            'ur' : unumpy.std_devs(r), # incerteza da distância
            'r0' : r[0].nominal_value, # distância inicial
            't0' : t[0].nominal_value, # distância inicial
            'tc' : t[-1].nominal_value + 1/60 # tempo de contato
        }
    return exp_data

def non_linear_regression(data_entry, A, B) -> [float]:
    t, r = data_entry['t'], data_entry['r']
    ut, ur = data_entry['ut'], data_entry['ur']
    r0, tc = data_entry['r0'], data_entry['tc']

    # f = lambda x : A*np.exp(-x) + B*np.exp(x)
    # def r(T,t):
    #     '''Função não linear r = r(t)'''
    #     return (r0/(f(tc/T[0]) - 1))*(f(tc/T[0]) - f(t/T[0]))
    def f(T,t):
        return (r0/(A*np.exp(-tc/T[0]) + B*np.exp(tc/T[0]) - 1))*(A*np.exp(-tc/T[0]) + B*np.exp(tc/T[0]) -(A*np.exp(-t/T[0]) + B*np.exp(t/T[0])))

    modelo = odr.Model(f)

    mydata = odr.RealData(t, r, sx=ut, sy=ur)
    myodr = odr.ODR(mydata, modelo, beta0=[(tc - t[0])*2/3])
    myoutput = myodr.run()

    tau = myoutput.beta[0]
    utau = myoutput.sd_beta[0]

    return tau, utau
def linear_regression(x, ux, y, uy):
    mydata = odr.RealData(x, y, sx=ux, sy=uy)
    myodr = odr.ODR(mydata, odr.models.unilinear)
    myoutput = myodr.run()

    A, B = myoutput.beta
    uA, uB = myoutput.sd_beta

    return A, uA, B, uB

def non_linear_model(data_entry, parameters = [0.001,0.001]) -> [float]:
    t, r = data_entry['t'], data_entry['r']
    ut, ur = data_entry['ut'], data_entry['ur']
    r0, tc = data_entry['r0'], data_entry['tc']

    def d(P,t):
        return (((P[0]/P[1])*tc + r0)/(1 - np.exp(-P[1]*tc)))*(np.exp(-P[1]*t) - 1) + (P[0]/P[1])*t + r0

    mymodel = odr.Model(d)

    mydata = odr.RealData(t, r, sx=ut, sy=ur)
    myodr = odr.ODR(mydata, mymodel, beta0=parameters)
    myoutput = myodr.run()

    C1, uC1 = myoutput.beta[0], myoutput.sd_beta[0]
    C2, uC2 = myoutput.beta[1], myoutput.sd_beta[1]

    return C1, uC1, C2, uC2
