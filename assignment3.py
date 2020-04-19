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
            1.50/10, 
            [i in list(range(10, 20+1)) for i in range(24)],
            ], 
        'heating': [ # Household heating
            8.00,
            8.00/24,
            [i in list(range(24)) for i in range(24)],
            ],
        'fridge': [ # fridge/freezer + small freezer
            3.00, 
            3.00/24,
            [i in list(range(24)) for i in range(24)],
            ],
        'stove': [ # Cooking stove
            2.40, 
            2.40,
            [i in list(range(5, 7+1)) + list(range(14, 22+1)) for i in range(24)],
            ],
        'tv': [ # Medium size TV
            0.15, 
            0.03,
            [i in list(range(4, 7+1)) + list(range(14, 22+1)) for i in range(24)],
            ],
        'computer': [ # 2 laptops
            0.60, 
            0.12,
            [i in list(range(4, 7+1)) + list(range(14, 22+1)) for i in range(24)],
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
            0.50, 
            [i in list(range(3, 7+1)) + list(range(14, 22+1)) for i in range(24)],
            ], 
        'dryer': [ # Clothes dryer
            2.50, 
            3.00,
            [i in list(range(3, 7+1)) + list(range(14, 22+1)) for i in range(24)],
            ],
        'ev': [ # Electric Vehicle
            9.90, 
            9.9/13, # energy demanded devided by 13operating hours
            [i in list(range(0, 6+1)) +  list(range(18, 23+1)) for i in range(24)],
            ], 
        'gc': [ # Game console
            0.27, 
            0.09,
            [i in list(range(18, 23+1)) for i in range(24)],
            ], 
        'phone': [ # Cellphone charge (x3)
            0.05, 
            0.015,
            [i in list(range(0, 3)) for i in range(24)],
            ],
        'coffee': [ # Coffee maker, 2 times/day
            0.53, 
            0.80,
            [i in list(range(3, 7+1)) + list(range(14, 18+1)) for i in range(24)],
            ], 
        'vacuum': [ # Vacuum cleaner
            0.23, 
            1.40,
            [i in list(range(3, 7+1)) + list(range(14, 23+1)) for i in range(24)],
            ], 
        'microwave': [ # 
            0.30, 
            1.20,
            [i in list(range(5, 7+1)) + list(range(14, 22+1)) for i in range(24)],
            ], 
        'wifi': [ # Router
            0.14, 
            0.006,
            [i in list(range(24)) for i in range(24)],
            ], 
        'ac': [ # Air-condition
            3.00, 
            1.00,
            [i in list(range(24)) for i in range(24)],
            ], 
        'waterheater': [ # 
            12.0, 
            4.00,
            [i in list(range(24)) for i in range(24)],
            ], 
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
    """Problem 1 - subclass
    """
    def __init__(self):
        super().__init__(
            app_names=['dishes', 'laundry', 'ev'],
            pricing = 'ToU',
            )
        self.set_time()
        self.optimise()
        
    def set_time(self):
        """Create peak and base timeslots for every app
        """
        self.apps['ts_p'] = self.apps['ts'].apply(lambda x: [ai and bi for ai, bi in zip(x, self.pricing_time)])
        self.apps['ts_b'] = self.apps['ts'].apply(lambda x: [ai and not bi for ai, bi in zip(x, self.pricing_time)])
        
    def optimise(self):
        """Run Optimisations
        
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
        print('A_eq:')
        print(A_eq)
        print('b_eq:')
        print(b_eq)
        # print('A_ub:')
        # print(A_ub)
        # print('b_ub:')
        # print(b_ub)
        print('bounds:')
        print(bounds)
        print('c:')
        print(c)
        print('results:')
        print(res)
        
                
        
if __name__ == "__main__":
    obj = Prob1()
    
