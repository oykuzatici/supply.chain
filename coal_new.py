# -*- coding: utf-8 -*-
"""coal_new.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SEF3PfPsmBsCgEFpVy-u7xFanlSa8SiP
"""

!pip install gurobipy

from gurobipy import GRB, Model
import random

# Supplier capacity limits
supplier_capacity = {'supplier1': 120, 'supplier2': 100, 'supplier3': 80}

# Shipping cost from supplier to factory
shipping_cost_supplier_to_factory = {
    ('supplier1', 'factory1'): 4,
    ('supplier1', 'factory2'): 6,
    ('supplier2', 'factory1'): 5,
    ('supplier2', 'factory2'): 3,
    ('supplier3', 'factory1'): 7,
    ('supplier3', 'factory2'): 4
}

# Customer list
customers = ['customer1', 'customer2']

# Shipping cost from factory to customer
shipping_cost_factory_to_customer = {
    ('factory1', 'customer1'): 20,
    ('factory1', 'customer2'): 35,
    ('factory2', 'customer1'): 25,
    ('factory2', 'customer2'): 30,
}

# Demand by product type for each customer
demand_negative = {
    'customer1': 50,
    'customer2': 40
}

demand_positive = {
    'customer1': 60,
    'customer2': 30
}

# Extract factory and supplier names from the data
factories = list(set(i[1] for i in shipping_cost_supplier_to_factory.keys()))
suppliers = list(set(i[0] for i in shipping_cost_supplier_to_factory.keys()))

# OPTIGUIDE CONSTRAINT CODE GOES HERE

model = Model("coal_distribution")

# Decision variables:
# x: shipment from suppliers to factories
x = model.addVars(shipping_cost_supplier_to_factory.keys(), vtype=GRB.INTEGER, name="x")

# y_negative: shipment of negative coal from factories to customers
y_negative = model.addVars(shipping_cost_factory_to_customer.keys(), vtype=GRB.INTEGER, name="y_negative")

# y_positive: shipment of positive coal from factories to customers
y_positive = model.addVars(shipping_cost_factory_to_customer.keys(), vtype=GRB.INTEGER, name="y_positive")

# Flow balance constraints: input to each factory equals output from that factory
for f in factories:
    model.addConstr(
        sum(x[i] for i in shipping_cost_supplier_to_factory if i[1] == f) ==
        sum(y_negative[j] + y_positive[j] for j in shipping_cost_factory_to_customer if j[0] == f),
        name=f"flow_balance_{f}"
    )

# Supplier capacity constraints
for s in suppliers:
    model.addConstr(
        sum(x[i] for i in shipping_cost_supplier_to_factory if i[0] == s) <= supplier_capacity[s],
        name=f"supplier_capacity_{s}"
    )

# Customer demand constraints for negative and positive coal
for c in customers:
    model.addConstr(
        sum(y_negative[j] for j in shipping_cost_factory_to_customer if j[1] == c) >= demand_negative[c],
        name=f"demand_negative_{c}"
    )
    model.addConstr(
        sum(y_positive[j] for j in shipping_cost_factory_to_customer if j[1] == c) >= demand_positive[c],
        name=f"demand_positive_{c}"
    )

# Factory production capacity constraints (sum of positive and negative shipments)
factory_capacity = {f: random.randint(100, 150) for f in factories}
for f in factories:
    model.addConstr(
        sum(y_negative[j] + y_positive[j] for j in shipping_cost_factory_to_customer if j[0] == f) <= factory_capacity[f],
        name=f"factory_capacity_{f}"
    )

# Production cost per unit for negative and positive coal at factories
cost_negative = {'factory1': 39.39, 'factory2': 39.39}
cost_positive = {'factory1': 39.39, 'factory2': 39.39}

# Hypothetical additional production costs
production_cost_negative = 5
production_cost_positive = 8

# Objective function: minimize total cost (supplier-to-factory + factory-to-customer + production costs)
model.setObjective(
    sum(shipping_cost_supplier_to_factory[i] * x[i] for i in shipping_cost_supplier_to_factory) +
    sum((shipping_cost_factory_to_customer[j] + cost_negative[j[0]] + production_cost_negative) * y_negative[j] for j in shipping_cost_factory_to_customer) +
    sum((shipping_cost_factory_to_customer[j] + cost_positive[j[0]] + production_cost_positive) * y_positive[j] for j in shipping_cost_factory_to_customer),
    GRB.MINIMIZE
)

# Solve the model
model.optimize()

# Print results if optimal solution found
if model.status == GRB.OPTIMAL:
    print(f"✅ Optimal solution found. Total cost: {model.ObjVal:.2f}")
    print("\nDecision Variables with positive shipment:")
    for v in model.getVars():
        if v.X > 0:
            print(f"{v.VarName} = {v.X}")
    print("\nFactory Capacities:")
    for f in factory_capacity:
        print(f"{f}: {factory_capacity[f]} units")
else:
    print("❌ No feasible solution found.")
