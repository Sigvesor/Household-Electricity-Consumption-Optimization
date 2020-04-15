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
    ## Appliances listet by name --  energy , power, 0perating hours
    # Non-shiftable appliances [kWh/day]
    non_shift_app = {
        'lighting': [ # Lightning between 10:00-20:00
            1.50, 
            [], 
            [i in list(range(10, 20+1)) for i in range(24)],
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
            [i in list(range(4, 6+1)) + list(range(14, 18+1)) for i in range(24)],
            ], 
        'laundry': [ # Laundry machine
            1.94, 
            .5, 
            [i in list(range(3, 7+1)) + list(range(14, 22+1)) for i in range(24)],
            ], 
        'dryer': [ # Clothes dryer
            2.50, 
            None,
            [],
            ],
        'ev': [ # Electric Vehicle
            9.90, 
            .5, 
            [i in list(range(0, 6+1)) +  list(range(18, 23+1)) for i in range(24)],
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
    # Pricing Schemes
    pricing = {
        'ToU': {
            'peak': 1, # €/kWh
            'base': .5, # €/kWh
            },
        }
    time_range = {
        'ToU': [i in list(range(17, 20+1)) for i in range(24)],
        }
        
    def __init__(self, app_names=None, pricing=None):
        self.apps = pd.DataFrame.from_dict(
            {key: self.apps[key] for key in app_names}, 
            orient='index',
            columns=['e', 'p', 'ts'],
            )
        self.pricing_time = self.time_range[pricing]
        self.pricing = self.pricing[pricing]
        

class Prob1(Optimisation):
    def __init__(self):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            pricing = 'ToU',
            )
        self.set_time()
        self.optimise()
        
    def set_time(self):
        self.apps['ts_p'] = self.apps['ts'].apply(lambda x: [ai and bi for ai, bi in zip(x, self.pricing_time)])
        self.apps['ts_b'] = self.apps['ts'].apply(lambda x: [ai and not bi for ai, bi in zip(x, self.pricing_time)])
        # if self.apps['ts'].apply(lambda x : sum(x)) is (self.apps['ts_p'].apply(lambda x : sum(x)) + self.apps['ts_b'].apply(lambda x : sum(x))):
        #     print('failed')
        
    def optimise(self):
        c = array([x * self.pricing['peak'] for x in self.apps['p']] + [x *self.pricing['base'] for x in self.apps['p']])
        # A_ub = np.eye(6)
        # b_ub = array([sum(x) for x in self.apps['ts_p']] + [sum(x) for x in self.apps['ts_b']])
        bounds = np.array([
            np.zeros(6), 
            np.concatenate(
                ([sum(x) for x in self.apps['ts_p']], [sum(x) for x in self.apps['ts_b']])
                )]
            ).transpose()
        A_eq = np.concatenate(([np.eye(3) * self.apps['p'].to_numpy()] * 2), axis=1)
        b_eq = array(self.apps['e'].tolist())
        res = linprog(
            c,
            # A_ub=A_ub,
            # b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            )
        print(res)
        
                
        
if __name__ == "__main__":
    obj = Prob1()
    # print(obj.apps)
        
    
