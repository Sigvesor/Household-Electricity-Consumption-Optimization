# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 11:47:19 2020

@author: alfredo
"""

import numpy as np
from numpy import array
import pandas as pd
import scipy as sp
from scipy.optimize import linprog
import matplotlib.pyplot as plt


class Optimisation:
    """Base Class for Assignment 3
    
    Appliances are listed as class elements, selected while initialising the problem related classes.
    
    Variables
    --------_
    app: dict of lists
        energy , power, timeslots (operating hours)
    pricing: <working>
    time_range: <working>
    """
    # Non-shiftable appliances [kWh/day]
    non_shift_apps = {
        'lighting': [ # Lightning between 10:00-20:00
            1.50, 
            1.5/11, 
            list(range(10, 19+1)),
            ], 
        'heating': [ # Household heating
            8.00,
            8/24,
            list(range(24)),
            ],
        'fridge': [ # fridge/freezer + small freezer
            3.00, 
            3/24,
            list(range(24)),
            ],
        'stove': [ # Cooking stove
            3.90, 
            2.40,
            list(range(6, 7+1)) + list(range(18, 19+1)),
            ],
        'tv': [ # Medium size TV
            .21, 
            .03,
            list(range(14, 22+1)),
            ],
        'computer': [ # 2 computers
            .60,
            .12,
            list(range(15, 22+1)),
            ],
        }
    # Shiftable appliances [    /day]
    shift_apps = {
        'dishes': [ # Dishwasher
            1.44, 
            .35, 
            list(range(4, 6+1)) + list(range(14, 18+1)),
            ], 
        'laundry': [ # Laundry machine
            1.94, 
            .5, 
            list(range(3, 6+1)) + list(range(14, 21+1)),
            ], 
        'dryer': [ # Clothes dryer
            2.50, 
            3,
            list(range(8, 22+1)),
            ],
        'ev': [ # Electric Vehicle
            9.90, 
            2,
            list(range(0, 6+1)) +  list(range(20, 23+1)),
            ], 
        'gc': [ # Game console
            0.27, 
            0.09,
            list(range(18, 22+1)),
            ], 
        'phone': [ # Cellphone charge (x3)
            0.05, 
            0.015,
            list(range(0, 5+1)) + list(range(22, 23+1)),
            ],
        'coffee': [ # Coffee maker, 2 times/day
            0.53, 
            0.80,
            list(range(6, 8+1)) + list(range(16, 18+1)),
            ], 
        'vacuum': [ # Vacuum cleaner
            0.23, 
            1.40,
            list(range(14, 21+1)),
            ], 
        'microwave': [ # 
            0.30, 
            1.20,
            list(range(17, 21+1)),
            ], 
        'ac': [ # Air-condition
            3.00, 
            1.00,
            list(range(24)),
            ], 
        'waterheater': [ # 
            12.0, 
            4.00,
            list(range(24)),
            ], 
        }
        
    def __init__(self, app_names=None, pricing=None):
        self.nr_of_hours = 24
        self.power_max = 5
        self.apps = pd.DataFrame.from_dict(
            self.apps, 
            orient='index',
            columns=['e', 'p', 'ts'],
            )
        self.apps['oh'] = self.apps['ts'].apply(lambda x: len(x))
        self.time_matrix = self._create_time_matrix(self.apps)
        if pricing:
            self.pricing = self._rtp_noise(
                pd.read_csv('nordpool_20200303.csv', decimal=',')[pricing][0:self.nr_of_hours].to_numpy() / 1000 # €/kWh
                )
            # self.pricing = pd.read_csv('nordpool_20200303.csv', decimal=',')[pricing][0:self.nr_of_hours].to_numpy() / 1000 # €/kWh
            self.non_shift_offset = self._compute_ineq_con_offest() 
        else:
            pricing_time = [i in list(range(17, 20+1)) for i in range(self.nr_of_hours)]
            self.pricing = [.1 if i else .05 for i in pricing_time] # €/kWh
            self.non_shift_offset = {
                'power': np.zeros(self.nr_of_hours),
                'pricing': np.zeros(self.nr_of_hours),
                }
        self.raw_result = []
        self.result = []
            
    def _create_time_matrix(self, apps):
        tmp = np.zeros((self.nr_of_hours, len(apps)))
        for idx1, (key, row) in enumerate(apps.iterrows()):
            for idx2 in row['ts']:
                tmp[idx2, idx1] = 1
        tmp = pd.DataFrame(tmp, columns=apps.index)
        return tmp
    
    def _resolve_res_matrix(self, res):
        if not res.success:
            print('optimisation not successfull')
            pass
        x = res.x
        res_time_wise = x.reshape(self.nr_of_hours, int(x.size / self.nr_of_hours), order='F')
        return res_time_wise
            
    def _conc_aeq_matrix(self, matrix):
        shape = matrix.shape
        n_col = shape[1]
        n_row = shape[0]
        tmp = np.array([])
        for i in range(n_col):
            if i == 0:
                tmp = np.eye(n_row) * matrix.T[i]
            else:
                tmp = np.concatenate((tmp, np.eye(n_row) * matrix.T[i]), axis=1)
        return tmp
    
    def _conc_aub_matrix(self, matrix):
        shape = matrix.shape
        n_col = shape[1]
        n_row = shape[0]
        tmp = np.zeros((n_row, n_col * n_row))
        for idx, row in enumerate(matrix):
            tmp[idx][idx * n_col:(1 + idx) * n_col] = row
        return tmp
        
    def _rtp_noise(self, pricing):
        np.random.seed(0)
        noise = np.random.randint(-100, 100, len(pricing)) / 100
        pricing += noise * pricing * .01
        return pricing
    
    def _compute_ineq_con_offest(self):
        apps = pd.DataFrame.from_dict(
            self.non_shift_apps, 
            orient='index',
            columns=['e', 'p', 'ts'],
            )
        time_matrix = self._create_time_matrix(apps).to_numpy()
        power = (time_matrix * apps['p'].to_numpy()).sum(axis=1)
        non_shift_offset = {
            'power': power,
            'pricing': power * self.pricing,
            }
        return non_shift_offset
    
    def execute(self):
        """Main method to execute optimisation"""
        raw_result = self.optimise()
        self.raw_result = raw_result
        power, pricing = self.resolve_result(raw_result)
        self.result = {
            'power': power,
            'pricing': pricing,
            }
        # self.plot_mode('pricing')
        # self.plot_mode('power')
        print('++++++++++++++++++++++++\nFinal c= ' + str(round(self.raw_result.fun,5)) + '€/day')
        
    def resolve_result(self, raw_result):
        """Resolving optimisation results"""
        res_time_wise = self._resolve_res_matrix(raw_result)
        res_power = res_time_wise * self.apps['p'].to_numpy()
        res_pricing = res_time_wise.T * self.pricing
        power = pd.DataFrame(
            res_power,
            columns=self.apps.index,
            )
        pricing = pd.DataFrame(
            res_pricing.T,
            columns=self.apps.index,
            )
        return power, pricing
    
    def optimise(self):
        """Run Optimisations
        TODO: linprog method: default not working, simplex does due at the moment
        
        Result
        ------
        x: list of x values (true operating hours for every app for either base or peak timer)
            op_dish_p, op_laun_p, op_ev_p, op_dish_b, op_laun_b, op_ev_b
        """
        time_matrix = self.time_matrix.to_numpy()
        power_matrix = time_matrix * self.apps['p'].to_numpy()
        price_matrix = power_matrix.T * self.pricing
        A_ub = self._conc_aeq_matrix(power_matrix)
        b_ub = np.subtract(np.ones(self.nr_of_hours) *  self.power_max, self.non_shift_offset['power'])
        A_eq = self._conc_aub_matrix(power_matrix.T)
        b_eq = self.apps['e'].to_numpy()
        c = price_matrix.ravel()
        bounds = tuple([(0, x) for x in time_matrix.T.ravel()])
        raw_result = linprog(
            c,
            A_eq=A_eq,
            b_eq=b_eq,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method='revised simplex',
            options={
                'disp':True, 
                'maxiter':5000,
                },
            )
        raw_result.fun= raw_result.fun + sum(self.non_shift_offset['pricing'])
        return raw_result
        
    def plot_mode(self, mode, figsize=(16,8)):
        """Plot either 'pricing' or 'power' hourly"""
        ylabel = {
            'pricing': 'hourly cost (EUR)',
            'power': 'power (kW)',
            }
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        axes = [ax1, ax2]
        data = self.result[mode]
        data = data.append(
            pd.DataFrame(data[-1:], index=[self.nr_of_hours], columns=data.columns)
            )
        data.plot(
            ax=axes[0],
            drawstyle="steps-post",
            linewidth=2,
            # legend=False,
            )
        tmp = {
            'non-shift': self.non_shift_offset[mode],
            'shift': self.result[mode].sum(axis=1),
            }
        tmp['total'] = tmp['non-shift'] + tmp['shift']
        # if mode is 'pricing':
        #     tmp['price'] = self.pricing
        data = pd.DataFrame(
            tmp
            )
        data = data.append(
            pd.DataFrame(data[-1:], index=[self.nr_of_hours], columns=data.columns)
            )
        data.plot(
            ax=axes[1],
            drawstyle="steps-post",
            linewidth=2,
            )
        if mode == 'pricing':
            tmp = pd.DataFrame(self.pricing, columns=['price'])
            tmp = tmp.append(
               pd.DataFrame(tmp[-1:], index=[self.nr_of_hours], columns=tmp.columns)
               )
            tmp.plot(
                ax=axes[1],
                secondary_y=['price'],
                drawstyle='steps-post',
                style='--',
                linewidth=1.5,
                )
            axes[1].right_ax.set_ylabel('price (EUR/kWh)')
        elif mode == 'power':
            tmp = pd.DataFrame([self.power_max]* len(data), columns=['max\_power'])
            tmp.plot(
                ax=axes[1],
                # secondary_y=['max_power'],
                drawstyle='steps-post',
                style='--',
                linewidth=1.5,
                )
        for ax in axes:
            ax.set_xticks(range(self.nr_of_hours+1))
            ax.set_xlabel('time of day (h)')
            ax.grid('on')
            # ax.legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
            ax.set_ylabel(ylabel[mode])
        return fig
        

class Prob1(Optimisation):
    """Problem 1 - subclass
    """
    def __init__(self):
        self.apps  = {key: self.shift_apps[key] for key in ['dishes', 'laundry', 'ev']}
        super().__init__(
            )
        self.power_max = 1
        self.execute()


class Prob2(Optimisation):
    """Problem 2 - subclass
    """
    def __init__(self, **kwargs):
        self.apps = self.shift_apps
        super().__init__(
            pricing=kwargs.get('data_name', 'Krsand'),
            )
        self.execute()
        # self.plot_operating_time()
        
    def plot_operating_time(self):
        data = self.apps['oh']
        fig = plt.figure()
        ax = fig.gca()
        data.plot(
            ax=ax,
            kind='bar',
            )

        
class Prob3(Optimisation):
    """Problem 3 - subclass
    """
    def __init__(self, **kwargs):
        n_housholds = 30
        self.apps = self.shift_apps
        super().__init__(
            pricing=kwargs.get('data_name', 'Krsand'),
            )
        self.power_max *= n_housholds *.7
        self.apps = pd.concat([self.apps]*n_housholds, keys=range(n_housholds))
        for key in self.non_shift_offset.keys():
            self.non_shift_offset[key] *= n_housholds
        self.apps = self.apps.drop([(i,'ev') for i in range(0,n_housholds,2)])
        self.time_matrix = self._create_time_matrix(self.apps)
        self.execute()
        # self.plot_single_housholds('power')
        self.plot_pricing()
        
    def plot_single_housholds(self, mode, idx=[0,1], figsize=(16,12)):
        """Plot single housholds with/without "ev"
        
        Parameters
        ----------
        mode: string
            either 'pricing' or 'power' for repective plots
        
        """
        ylabel = {
            'pricing': 'hourly cost (EUR)',
            'power': 'power (kW)',
            }
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        axes = [ax1, ax2]
        data = self.result[mode]
        data1 = data.get([idx[0]])
        data1 = pd.DataFrame(data1.to_numpy(), columns=[i[1] for i in data1.columns])
        data2 = data.get([idx[1]])
        data2 = pd.DataFrame(data2.to_numpy(), columns=[i[1] for i in data2.columns])
        data1 = data1.append(
            pd.DataFrame(data1[-1:], index=[self.nr_of_hours], columns=data1.columns)
            )
        data1.plot(
            ax=axes[0],
            drawstyle="steps-post",
            linewidth=2,
            # legend=False,
            )
        axes[0].legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
        data2 = data2.append(
            pd.DataFrame(data2[-1:], index=[self.nr_of_hours], columns=data2.columns)
            )
        data2.plot(
            ax=axes[1],
            drawstyle="steps-post",
            linewidth=2,
            # legend=False,
            )
        axes[1].legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
        for ax in axes:
            ax.set_xticks(range(self.nr_of_hours+1))
            ax.set_xlabel('time of day (h)')
            ax.grid('on')
            # ax.legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
            ax.set_ylabel(ylabel[mode])
        return fig
        
    def plot_pricing(self, figsize=(16,8)):
        """Plot pricing curve"""
        ylabel = {
            'pricing': 'hourly cost (EUR)',
            'power': 'power (kW)',
            }
        fig = plt.figure(figsize=figsize)
        # ax1 = fig.add_subplot(2, 1, 1)
        # ax2 = fig.add_subplot(2, 1, 2)
        ax = fig.gca()
        tmp = self.result['pricing']
        tmp = {
            'non-shift': self.non_shift_offset['pricing'],
            'shift': tmp.sum(axis=1),
            }
        tmp['total'] = tmp['non-shift'] + tmp['shift']
        data = pd.DataFrame(
            tmp
            )
        data = data.append(
            pd.DataFrame(data[-1:], index=[self.nr_of_hours], columns=data.columns)
            )
        data.plot(
            ax=ax,
            drawstyle="steps-post",
            linewidth=2,
            )
        tmp = pd.DataFrame(self.pricing, columns=['price'])
        tmp = tmp.append(
           pd.DataFrame(tmp[-1:], index=[self.nr_of_hours], columns=tmp.columns)
           )
        tmp.plot(
            ax=ax,
            secondary_y=['price'],
            drawstyle='steps-post',
            style='--',
            linewidth=1.5,
            )
        ax.right_ax.set_ylabel('price (EUR/kWh)')
        ax.set_xticks(range(self.nr_of_hours+1))
        ax.set_xlabel('time of day (h)')
        ax.grid('on')
        # ax.legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
        ax.set_ylabel(ylabel['pricing'])
        return fig
        
if __name__ == "__main__":
    # obj = Prob1_simple()
    # obj = Prob1()
    # obj = Prob2()
    # obj = Prob2(data_name='Ger')
    obj = Prob3()
