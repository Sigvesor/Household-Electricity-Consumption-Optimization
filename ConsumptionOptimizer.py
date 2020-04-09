# -*- coding: utf-8 -*-
"""
Created on Wed Apr 8 17:02:31 2020

@author: Sigve Sørensen & Ernst-Martin Buduschin
"""

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

class ConsumptionOptimizer:
    """Scheduling of household appliance' for cost minimization"""
    
    def __init__(self):
        
        # Non-shiftable appliances [kWh/day]
        self.non_shift_app = {
            'lighting': 1.50, # Lightning between 10:00-20:00
            'heating': 8.00, # Household heating
            'fridge': 3.00, # fridge/freezer + small freezer
            'stove': 3.90, # Cooking stove
            'tv': 0.40, # Medium size TV
            'computer': 1.20, # 2 computers
            }
        
        # Shiftable appliances [kWh/day]
        self.shift_app = {
            'dishes': 1.44, # Dishwasher
            'laundry': 1.94, # Laundry machine
            'dryer': 2.50, # Clothes dryer
            'ev': 9.90, # Electric Vehicle
            'vg': 0.09, # Game console
            'phone': 0.04, # Cellphone charge (x3) - 5W*3h
            'coffee': 0.28, # Coffee-maker - 800W*0.17h*2
            'vacuum': 0.23, # Vacuum cleaner - 1400W*0.17h
            'microwave': 0.30, # 1200W*0.25h
            'wifi': 0.14, # Router - 6W*24h
            'ac': 3.00, # Air-condition - 1kW*3h
            'waterheater': 12.0, # 4kW*3h
            }
        
        # Household appliances
        self.apps = {**self.non_shift_app, **self.shift_app}

        # Define timespan of 24 hours
        self.period = pd.date_range('2020-05-01', periods=25, freq='60min')
        self.price = pd.DataFrame()
        self.price['Datetime'] = self.period
        
        # Electric price scheme of Problem 1
        self.price['Price'] = np.empty(25)
        
        for idx, val in enumerate(self.price['Datetime']):
            if idx < 17 or idx > 20:
                self.price['Price'].iloc[idx] = 0.5
            else:
                self.price['Price'].iloc[idx] = 1.0
        self.price.set_index('Datetime', inplace=True)
        
    
    def plot_pricing_scheme(self):
        """Plot electricity pricing scheme"""
        
        self.price.plot()
        plt.show()
        

if __name__ == "__main__":
    c = ConsumptionOpt()
    c.plot_pricing_scheme()
    