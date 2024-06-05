from gurobipy import Model, GRB, quicksum

# Initialize the model
m = Model("Time_Extended_Evacuation_Model")

#-----------------------Example dataset---------------------#

#**********SETS*********#

# Set of Nodes in the System
nodes = ['A', 'B', 'C', 'D']

# Set of Arcs in the System
arcs = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')] 

# Set of Time steps
time_steps = range(3)  

# Set of Origins
origins = ['A', 'B']  

# Set of Destinations/Shelters
destinations = ['C', 'D']  

# Time-extended copies of Nodes
time_extended_origins = [(o, t) for o in origins for t in time_steps]

# Time-extended copies of Destinations
time_extended_destinations = [(d, t) for d in destinations for t in time_steps]

# Set of Resources
resources = ['R1', 'R2'] 

# Set of Deployable Nodes
deployable_nodes = nodes

#**********PARAMETERS*********#

# Evacuation demand at origin o ∈ O
q_o = {
       'A': 20,
       'B': 30
       }

# Capacity of arc a ∈ A
q_a = {
       ('A', 'B'): 15, 
       ('B', 'C'): 30, 
       ('C', 'D'): 40, 
       ('D', 'A'): 25,
       }  

# Additional capacity if a resource is deployed
delta_q_a = {a: 50 for a in arcs} 

# Risk level on arc a ∈ A at time t ∈ T (Risk level might vary by arc and time step)
c_a_t = {(a, t): 0.1*t for a in arcs for t in time_steps}

#**********PARAMETERS*********#

#-----------------------Example dataset---------------------#

#---------------------Decision variables--------------------#

# 1 if origin o is assigned to destination d, 0 otherwise
x_od = {}
for o in origins:
    for d in destinations:
        var_name = f"x_{o}_{d}"
        x_od[(o, d)] = m.addVar(vtype=GRB.BINARY, name=var_name)

# 1 if resource p is deployed to location n at time t, 0 otherwise
z_nt = m.addVars(nodes, time_steps, vtype=GRB.BINARY, name="z_nt")
w_ot = m.addVars(origins, time_steps, vtype=GRB.BINARY, name="w_ot")
y_ot = m.addVars(origins, time_steps, vtype=GRB.BINARY, name="y_ot")
r_at = m.addVars(arcs, time_steps, vtype=GRB.BINARY, name="r_at")
f_ao = m.addVars(arcs, origins, vtype=GRB.CONTINUOUS, name="f_ao")

#---------------------Decision variables--------------------#

# Parameters - initialize c_ao correctly
c_ao = {(a, o): 0.1 for a in arcs for o in origins}

# Objective Function
objective_expr = quicksum(c_ao[(a, o)] * f_ao[a, o] for a in arcs for o in origins)
m.setObjective(objective_expr, GRB.MINIMIZE)

# Constraints
# Flow conservation
for n in nodes:
    for t in time_steps:
        m.addConstr(
            quicksum(f_ao[(i, n), o] for i, n in arcs if (i, n) in arcs for o in origins) ==
            quicksum(f_ao[(n, j), o] for n, j in arcs if (n, j) in arcs for o in origins), 
            "flow_conservation_{}_{}".format(n, t)
        )

# Capacity constraints
for a in arcs:
    for t in time_steps:
        m.addConstr(
            quicksum(f_ao[a, o] for o in origins) <= q_a[a] * (1 - r_at[a, t]) + 
            quicksum(delta_q_a[a] * z_nt[n, t] for n in nodes) + (q_a[a] + delta_q_a[a]) * r_at[a, t],
            "capacity_{}_{}".format(a, t)
        )

# Resource deployment limits
for n in nodes:
    for t in time_steps:
        m.addConstr(z_nt[n, t] <= 1, "resource_limit_{}_{}".format(n, t))

# Optimize the model
m.optimize()

# Output results
for v in m.getVars():
    if v.x > 0.1:  # Small threshold to ignore essentially zero values
        print(f'{v.varName}: {v.x}')

# Print the objective value
print(f'Objective Value: {m.objVal}')
