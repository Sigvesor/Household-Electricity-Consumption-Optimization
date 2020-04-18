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
            None,
            [],
            ],
        'fridge': [ # fridge/freezer + small freezer
            3.00, 
            None,
            [],
            ],
        'stove': [ # Cooking stove
            3.90, 
            None,
            [],
            ],
        'tv': [ # Medium size TV
            0.40, 
            None,
            [],
            ],
        'computer': [ # 2 computers
            1.20, 
            None,
            [],
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
            None,
            [],
            ],
        'ev': [ # Electric Vehicle
            9.90, 
            .8, # energy demanded devided by 13operating hours
            list(range(0, 6+1)) +  list(range(18, 23+1)),
            ], 
        # 'vg': 0.09, # Game console
        # 'phone': 0.04, # Cellphone charge (x3) - 5W*3h
        # 'coffee': 0.28, # Coffee-maker - 800W*0.17h*2
        # 'vacuum': 0.23, # Vacuum cleaner - 1400W*0.17h
        # 'microwave': 0.30, # 1200W*0.25h
        # 'wifi': 0.14, # Router - 6W*24h
        # 'ac': 3.00, # Air-condition - 1kW*3h
        # 'waterheater': 12.0, # 4kW*3h
        }
    apps = {**non_shift_app, **shift_app}
        
    def __init__(self, app_names=None, pricing=None):
        self.apps = pd.DataFrame.from_dict(
            self.apps if not app_names else {key: self.apps[key] for key in app_names}, 
            orient='index',
            columns=['e', 'p', 'ts'],
            )
        self.apps['oh'] = self.apps['ts'].apply(lambda x: len(x))
        
    def _split_app_matrix(self, tmp):
        ts = {}
        p_val = self._conc_app_matrix()
        for idx, (key, row)  in enumerate(self.apps.iterrows()):
            if idx != 0:
                start = np.where(p_val[idx-1] != 0)[0][-1] + 1
            else:
                start = idx
            ts[key] = array([row['ts'], tmp[start:start + row['oh']].tolist()]).transpose()
        return ts
            
    def _conc_app_matrix(self):
        apps = self.apps
        n_variables = sum(apps['oh'])
        tmp = np.zeros((len(apps), n_variables))
        for idx, item in enumerate(apps['oh']):
            if idx != 0:
                start = np.where(tmp[idx-1] != 0)[0][-1] + 1
            else:
                start = idx
            tmp[idx, start:start + item] = 1
        return tmp.transpose()
    
    def _conc_upper_bounds_matrix(self):
        tmp = np.zeros((24, len(self.apps)))
        for idx1, (key, row) in enumerate(self.apps.iterrows()):
            for idx2 in row['ts']:
                tmp[idx2, idx1] = 1
        return tmp
    
    def optimise(self):
        """Run Optimisations
        TODO: linprog method: default not working, simplex does due at the moment
        
        Result
        ------
        x: list of x values (true operating hours for every app for either base or peak timer)
            op_dish_p, op_laun_p, op_ev_p, op_dish_b, op_laun_b, op_ev_b
        """
        app_matrix = self._conc_app_matrix()
        k = []
        for idx, row in self.apps.iterrows():
            k = k + [self.pricing[i] * row['p'] for i in row['ts']]
        k = app_matrix * self.pricing
        c = array(k)
        # A_ub = self._conc_upper_bounds_matrix()
        # b_ub = np.ones((24, 1)) * 20
        bounds = tuple([(0, 1)] * len(c))
        A_eq = app_matrix * self.apps['p'].to_numpy()
        b_eq = self.apps['e'].to_numpy().transpose()
        res = linprog(
            c,
            A_eq=A_eq,
            b_eq=b_eq,
            # A_ub=A_ub,
            # b_ub=b_ub,
            bounds=bounds,
            method='simplex',
            options={
                'disp':True, 'maxiter':5000
                },
            )
        res_var = self._split_app_matrix(res.x)        
        # print('cost: ' + str(res.fun) + ' €/d')
        # print('results:')
        # print(res)
        # print(res_var)
    
    
class Prob1_simple(Optimisation):
    """Problem 1 - subclass
    """
    def __init__(self):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            )
        self.pricing_time = [i in list(range(17, 20+1)) for i in range(24)]
        self.pricing = {
            'peak': .1, # €/kWh
            'base': .05, # €/kWh
            }
        self.apps['ts'] = self.apps['ts'].apply(lambda x: [i in x for i in range(24)])
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
        print('cost: ' + str(res.fun) + ' €/d')
        # print('A_eq:')
        # print(A_eq)
        # print('b_eq:')
        # print(b_eq)
        # print('A_ub:')
        # print(A_ub)
        # print('b_ub:')
        # print(b_ub)
        # print('bounds:')
        # print(bounds)
        # print('c:')
        # print(c)
        # print('results:')
        # print(res)
        

class Prob1(Optimisation):
    """Problem 1 - subclass
    """
    def __init__(self):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            )
        pricing_time = [i in list(range(17, 20+1)) for i in range(24)]
        self.pricing = [.1 if i else .05 for i in pricing_time] # €/kWh
        self.optimise()
    
        
class Prob2(Optimisation):
    def __init__(self, data_name='Krsand'):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            )
        self.pricing = pd.read_csv('nordpool_20200303.csv', decimal=',')[data_name][0:24].to_numpy() / 1000 # €/kWh
        self.rtp_noise()
        self.optimise()
    
    def rtp_noise(self):
        noise = np.random.randint(-100, 100, len(self.pricing)) / 100
        self.pricing += noise * self.pricing * .1
        
class Prob3(Optimisation):
    def __init__(self, data_name='Krsand'):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            )
        n_housholds = 30
        self.apps = pd.concat([self.apps]*n_housholds, keys=range(n_housholds))
        self.pricing = pd.read_csv('nordpool_20200303.csv', decimal=',')[data_name][0:24] / 1000 # €/kWh
        self.optimise()
        
        
        
if __name__ == "__main__":
    # obj = Prob1_simple()
    # obj = Prob1()
    obj = Prob2()
    # obj = Prob2(data_name='Ger')
    # obj = Prob3()
    
