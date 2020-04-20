#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 18:29:32 2020

@author: alfredo
"""
from assignment3 import Prob1, Prob2, Prob3

# def print_app_table():
#     obj = Prob2()
#     apps = obj.apps
#     app_names = apps.index
#     strng = [
#         [' & '.join([col for col in app_names]) + '\\\n'],
#         [' & '.join([val for ])]
#         ]
#     print(strng, file=open(loc + 'values/' + 'test_size.tex', 'w'),
#         )

def plot_prob1():
    import matplotlib as mp
    import matplotlib.pyplot as plt
    obj = Prob1()
    loc = '../code_report/'
    size = 25
    pgf_with_latex = {                      # setup matplotlib to use latex for output
        "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
        "text.usetex": True,                # use LaTeX to write all text
        "font.family": 'serif',
        "font.serif": [],                   # blank entries should cause plots 
        "font.sans-serif": [],              # to inherit fonts from the document
        "font.monospace": [],
        "axes.labelsize": size,               # LaTeX default is 10pt font.
        "font.size": size,
        "legend.fontsize": size,               # Make the legend/label fonts 
        "xtick.labelsize": size,               # a little smaller
        "ytick.labelsize": size,
        # "figure.figsize": (12, 8),     # default fig size of 0.9 textwidth
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts 
            r"\usepackage{eurosym}",
            r"\usepackage[T1]{fontenc}",        # plots will be generated
            r"\usepackage[detect-all,locale=DE]{siunitx}",
            ]                                   # using this preamble
        }
    mp.rcParams.update(pgf_with_latex)
    for mode in ['power', 'pricing']:
        fig = obj.plot_mode(mode)
        fig.savefig(loc + 'figures/prob1/' + mode + '.pgf')
    
    plt.rcParams['axes.prop_cycle'] = plt.rcParamsDefault['axes.prop_cycle']
    
def plot_prob2():
    import matplotlib as mp
    import matplotlib.pyplot as plt
    obj = Prob2()
    loc = '../code_report/'
    size = 20
    pgf_with_latex = {                      # setup matplotlib to use latex for output
        "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
        "text.usetex": True,                # use LaTeX to write all text
        "font.family": 'serif',
        "font.serif": [],                   # blank entries should cause plots 
        "font.sans-serif": [],              # to inherit fonts from the document
        "font.monospace": [],
        "axes.labelsize": size,               # LaTeX default is 10pt font.
        "font.size": size,
        "legend.fontsize": size,               # Make the legend/label fonts 
        "xtick.labelsize": size,               # a little smaller
        "ytick.labelsize": size,
        # "figure.figsize": (12, 8),     # default fig size of 0.9 textwidth
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts 
            r"\usepackage{eurosym}",
            r"\usepackage[T1]{fontenc}",        # plots will be generated
            r"\usepackage[detect-all,locale=DE]{siunitx}",
            ]                                   # using this preamble
        }
    mp.rcParams.update(pgf_with_latex)
    for mode in ['power', 'pricing']:
        fig = obj.plot_mode(mode, figsize=(16,12))
        fig.axes[0].legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
        # plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        fig.savefig(loc + 'figures/prob2/' + mode + '.pgf')
    
    plt.rcParams['axes.prop_cycle'] = plt.rcParamsDefault['axes.prop_cycle']
    
    
def plot_prob3():
    import matplotlib as mp
    import matplotlib.pyplot as plt
    obj = Prob3()
    loc = '../code_report/'
    size = 20
    pgf_with_latex = {                      # setup matplotlib to use latex for output
        "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
        "text.usetex": True,                # use LaTeX to write all text
        "font.family": 'serif',
        "font.serif": [],                   # blank entries should cause plots 
        "font.sans-serif": [],              # to inherit fonts from the document
        "font.monospace": [],
        "axes.labelsize": size,               # LaTeX default is 10pt font.
        "font.size": size,
        "legend.fontsize": size,               # Make the legend/label fonts 
        "xtick.labelsize": size,               # a little smaller
        "ytick.labelsize": size,
        # "figure.figsize": (12, 8),     # default fig size of 0.9 textwidth
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts 
            r"\usepackage{eurosym}",
            r"\usepackage[T1]{fontenc}",        # plots will be generated
            r"\usepackage[detect-all,locale=DE]{siunitx}",
            ]                                   # using this preamble
        }
    mp.rcParams.update(pgf_with_latex)
    idx = [0,1]
    for mode in ['power', 'pricing']:
        fig = obj.plot_single_housholds(mode, idx=idx)
        fig.savefig(loc + 'figures/prob3/' + mode + 'h' + str(idx[0]) + 'h' + str(idx[1]) + '.pgf')
    fig = obj.plot_pricing()
    fig.savefig(loc + 'figures/prob3/pricing.pgf')

    plt.rcParams['axes.prop_cycle'] = plt.rcParamsDefault['axes.prop_cycle']


if __name__ == "__main__":
    # obj = Prob1_simple()
    # obj = Prob1()
    # obj = Prob2
    # obj = Prob2(data_name='Ger')
    # obj = Prob3()
    # print_app_table()
    # plot_prob1()
    # plot_prob2()
    plot_prob3()
    