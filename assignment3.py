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
    non_shift_app = {
        'lighting': [ # Lightning between 10:00-20:00
            1.50, 
            1.5/11, 
            list(range(10, 20+1)),
            ], 
        'heating': [ # Household heating
            8.00,
            8/24,
            list(range(10, 20+1)),
            ],
        'fridge': [ # fridge/freezer + small freezer
            3.00, 
            3/24,
            list(range(24)),
            ],
        'stove': [ # Cooking stove
            3.90, 
            2.40,
            list(range(5, 7+1)) + list(range(14, 22+1)),
            ],
        'tv': [ # Medium size TV
            .15, 
            .03,
            list(range(4, 7+1)) + list(range(14, 22+1)),
            ],
        'computer': [ # 2 computers
            .60,
            .12,
            list(range(4, 7+1)) + list(range(14, 22+1)),
            ],
        }
    # Shiftable appliances [kWh/day]
    shift_app = {
        'dishes': [ # Dishwasher
            1.44, 
            .35, 
            list(range(4, 6+1)) + list(range(14, 18+1)),
            ], 
        'laundry': [ # Laundry machine
            1.94, 
            .5, 
            list(range(3, 7+1)) + list(range(14, 22+1)),
            ], 
        'dryer': [ # Clothes dryer
            2.50, 
            3,
            list(range(3, 7+1)) + list(range(14, 22+1)),
            ],
        'ev': [ # Electric Vehicle
            9.90, 
            3, # energy demanded devided by 13operating hours
            list(range(0, 6+1)) +  list(range(18, 23+1)),
            ], 
        'gc': [ # Game console
            0.27, 
            0.09,
            list(range(18, 23+1)),
            ], 
        'phone': [ # Cellphone charge (x3)
            0.05, 
            0.015,
            list(range(0, 5+1)) + list(range(22, 23+1)),
            ],
        'coffee': [ # Coffee maker, 2 times/day
            0.53, 
            0.80,
            list(range(5, 9+1)) + list(range(14, 18+1)),
            ], 
        'vacuum': [ # Vacuum cleaner
            0.23, 
            1.40,
            list(range(14, 22+1)),
            ], 
        'microwave': [ # 
            0.30, 
            1.20,
            list(range(6, 8+1)) + list(range(14, 22+1)),
            ], 
        # 'wifi': [ # Router
        #     0.14, 
        #     0.006,
        #     list(range(24)),
        #     ], 
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
    # apps = {**non_shift_app, **shift_app}
    apps = shift_app
        
    def __init__(self, app_names=None, pricing=None):
        self.nr_of_hours = 24
        self.power_max = 10
        self.apps = pd.DataFrame.from_dict(
            self.apps if not app_names else {key: self.apps[key] for key in app_names}, 
            orient='index',
            columns=['e', 'p', 'ts'],
            )
        self.apps['oh'] = self.apps['ts'].apply(lambda x: len(x))
        self.time_matrix = self._create_time_matrix()
        if pricing:
            # self.pricing = self._rtp_noise(
            #     pd.read_csv('nordpool_20200303.csv', decimal=',')[pricing][0:self.nr_of_hours].to_numpy() / 1000 # €/kWh
            #     )
            self.pricing = pd.read_csv('nordpool_20200303.csv', decimal=',')[pricing][0:self.nr_of_hours].to_numpy() / 1000 # €/kWh
        else:
            pricing_time = [i in list(range(17, 20+1)) for i in range(self.nr_of_hours)]
            self.pricing = [.1 if i else .05 for i in pricing_time] # €/kWh
        self.raw_result = []
        self.result = []
            
    def _create_time_matrix(self):
        tmp = np.zeros((self.nr_of_hours, len(self.apps)))
        for idx1, (key, row) in enumerate(self.apps.iterrows()):
            for idx2 in row['ts']:
                tmp[idx2, idx1] = 1
        tmp = pd.DataFrame(tmp, columns=self.apps.index)
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
        noise = np.random.randint(-100, 100, len(pricing)) / 100
        pricing += noise * pricing * .1
        return pricing
    
    def execute(self):
        raw_result = self.optimise()
        self.raw_result = raw_result()
        power, pricing = self.resolve_result(raw_result)
        self.result = {
            'power': power,
            'pricing': pricing,
            }
        self.plot_time_wise(power)
        
    def resolve_result(self, raw_result):
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
        b_ub = np.ones(self.nr_of_hours) *  self.power_max
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
        # print(raw_result.slack)
        return raw_result
        
    def plot_time_wise(self, data):
        fig = plt.figure(figsize=(18,6))
        ax = fig.gca()
        data.plot(
            ax=ax,
            drawstyle="steps-post",
            linewidth=2,
            legend=False,
            )
        ax.set_xticks(range(self.nr_of_hours))


class Prob1_simple(Optimisation):
    """Problem 1 - subclass
    """
    def __init__(self):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            )
        self.pricing_time = [i in list(range(17, 20+1)) for i in range(self.nr_of_hours)]
        self.pricing = {
            'peak': .1, # €/kWh
            'base': .05, # €/kWh
            }
        self.apps['ts'] = self.apps['ts'].apply(lambda x: [i in x for i in range(self.nr_of_hours)])
        self.apps['ts_p'] = self.apps['ts'].apply(lambda x: [ai and bi for ai, bi in zip(x, self.pricing_time)])
        self.apps['ts_b'] = self.apps['ts'].apply(lambda x: [ai and not bi for ai, bi in zip(x, self.pricing_time)])
        self.optimise()
        
    def optimise(self):
        """Run Optimisations
        TODO: linprog method: default not working, simplex does due at the moment
        
        Result
        ------
        x: list of x values (true operating hours for every app for either base or peak timer)
            op_dish_p, op_laun_p, op_ev_p, op_dish_b, op_laun_b, op_ev_b
        """
        c = array([x * self.pricing['peak'] for x in self.apps['p']] + [x *self.pricing['base'] for x in self.apps['p']])
        # A_ub = np.eye(6) 
        # b_ub = array([sum(x) for x in self.apps['ts_p']] + [sum(x) for x in self.apps['ts_b']])
        # bounds = np.array([
        #     np.zeros(6), 
        #     np.concatenate(
        #         ([sum(x) for x in self.apps['ts_p']], [sum(x) for x in self.apps['ts_b']])
        #         )]
        #     ).transpose().tolist()
        bounds = tuple((0, sum(x)) for x in self.apps['ts_p']) + tuple((0, sum(x)) for x in self.apps['ts_b'])
        A_eq = np.concatenate(([np.eye(3) * self.apps['p'].to_numpy()] * 2), axis=1)
        b_eq = array(self.apps['e'].tolist())
        res = linprog(
            c,
            # A_ub=A_ub,
            # b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method='simplex',
            )
        

class Prob1(Optimisation):
    """Problem 1 - subclass
    """
    def __init__(self):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            )
        self.execute()


class Prob2(Optimisation):
    def __init__(self, **kwargs):
        super().__init__(
            # app_names=['dishes', 'laundry', 'ev'],
            pricing=kwargs.get('data_name', 'Krsand'),
            )
        self.execute()

        
class Prob3(Optimisation):
    def __init__(self, **kwargs):
        super().__init__(
            # app_names=['dishes', 'laundry', 'ev'],
            pricing=kwargs.get('data_name', 'Krsand'),
            )
        n_housholds = 30
        self.power_max *= n_housholds
        self.apps = pd.concat([self.apps]*n_housholds, keys=range(n_housholds))
        self.time_matrix = self._create_time_matrix()
        self.execute()
        
        
        
if __name__ == "__main__":
    # obj = Prob1_simple()
    # obj = Prob1()
    # obj = Prob2()
    # obj = Prob2(data_name='Ger')
    obj = Prob3()
    
