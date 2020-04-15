## Household electricity consumption optimization
Optimized scheduling for minimization of household appliance electricity cost.

• Appliances with strict consumption scheduling (non-shiftable appliances) in each household
− Lighting: (daily usage for standard bulbs: 1.00-2.00 kWh from 10:00 - 20:00)
− Heating: (daily usage: 6.4-9.6 kWh including floor heating)
− Refrigerator- freezer (daily usage: 1.32-3.96 kWh, depending on the number of refrigerators in the house; Consumption for 1 refrigerator including freezer = 1.32 kWh)
− Electric stove (daily usage: 3.9 kWh)
− TV: (daily usage: 0.15-0.6 kWh depending on the TV size for 5 hours of use)
− Computer including desktop(s), laptop(s) (Number: 1-3; daily 0.6kWh per day per computer)

• Consumption of shiftable appliances
− Dishwasher: (daily usage: 1.44 kWh)
− Laundry machine: (daily usage: 1.94 kWh)
− Cloth dryer: (daily usage: 2.50 kWh)
− Electric Vehicle (EV): (daily usage: 9.9 kWh)

In a residential area, without any intelligent scheduling, the power demand is usually light-to-moderate
during mornings, higher during evenings and low during nights. Considering this, we need to
assign the time slots in hours as required for the non-shiftable appliances and provide a range of
possible time slots for operating the shiftable appliances.

### Problem 1: 
We have a simple household that only has three appliances: a washing machine, an
EV and a dishwasher. We assume the time-of-Use (ToU) pricing scheme: 1 NOK/kWh for peak
hour and 0.5 NOK/kWh for off-peak hours. Peak hours are in the range of 5:00 pm - 8:00 pm while
all other time slots are off-peak hours. Design the strategy to use these appliances to have minimum
energy cost.

Calculate the minimal energy consumption and explain the main considerations to
the developed strategy.

### Problem 2:
We have a household with all non-shiftable appliances and all shiftable appliances
(see the two lists aforementioned). In addition to these, please choose a random combination of
appliances such as coffee maker, ceiling fan, hair dryer, toaster, microwave, router, cellphone
charger, cloth iron, separate freezer(s), etc., for the household. Please refer to [2] to add typical
energy consumption values for the appliances. Please use Real-Time Pricing (RTP) scheme as
follows: using a random function to generate the pricing curve in a day. The pricing curve should
consider higher price in the peak-hours and lower price in the off-peak hours. Compute the best
strategy to schedule the use of the appliances and write a program in order to minimize energy
cost. For more information on RTP, please consider consulting Nordpool.

The formulation of the demand response as an optimization problem, e.g., linear
programming problem. Please use a figure to show the pricing curve. Please explain on how
the problem is solved and probably draw the flowchart to illustrate the main algorithm(s).

### Problem 3:
We consider a small neighborhood that has 30 households. Each household has the
same setting as that in problem 2. but we assume that only a fraction of the households owns an
EV. Please use the already mentioned Real-Time Pricing (RTP) scheme. Compute the best strategy
for scheduling the appliances and write a program in order to minimize energy cost in the
neighborhood.

The formulation of the demand response as an optimization problem. Please use a
figure to show the pricing curve. Please explain how the problem is solved and you may draw
the flowchart to illustrate the main algorithms.
