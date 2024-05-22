from gurobipy import Model, GRB, quicksum

#Initialize the model
m = Model("Time_Extended_Evacuation_Model")

#-----------------------Example dataset---------------------#


#**********SETS*********#

#Set of Nodes in the System
nodes = ['A', 'B', 'C', 'D']

#Set of Arcs in the System
arcs = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')] 

#Set of Time steps
time_steps = range(3)  

#Set of Scenarios
scenarios = range(2) 

#Set of Origins
origins = ['A', 'B']  

#Set of Destinations/Shelters
destinations = ['C', 'D']  

#Time-extended copies of Nodes
time_extended_origins = [(o, t) for o in origins for t in time_steps]

#Time-extended copies of Destinations
time_extended_destinations = [(d, t) for d in destinations for t in time_steps]

#Set of Resources
resources = ['R1', 'R2'] 

#Set of Deployable Nodes
deployable_nodes = nodes

#Set of identical/indistinguishable scenarios by time t;
indistinct_scenarios = {
    0: [0, 1],  # At time step 0, scenarios 0 and 1 are indistinguishable
    1: [0, 1],
    2: [0, 1]
}

#**********SETS*********#

#**********PARAMETERS*********#

#Evacuation demand at origin o ∈ O
q_o = {
       'A': 20,
       'B': 30
       }

#Capacity of arc a ∈ A
q_a = {
       ('A', 'B'): 15, 
       ('B', 'C'): 30, 
       ('C', 'D'): 40, 
       ('D', 'A'): 25,
       }  

#Additional capacity if a resource is deployed
delta_q_a = {a: 50 for a in arcs} 

#Risk level on arc a ∈ A at time t ∈ T in scenario s ∈ S (Risk level might vary by arc, time step, and scenario)
c_a_t_s = {(a, t, s): 0.1*t + 0.05*s for a in arcs for t in time_steps for s in scenarios}

#**********PARAMETERS*********#

#-----------------------Example dataset---------------------#

# Decision variables
x_od = m.addVars(origins, destinations, vtype=GRB.BINARY, name="x_od")
z_nts = m.addVars(nodes, time_steps, scenarios, vtype=GRB.BINARY, name="z_nts")
w_ots = m.addVars(origins, time_steps, scenarios, vtype=GRB.BINARY, name="w_ots")
y_ots = m.addVars(origins, time_steps, scenarios, vtype=GRB.BINARY, name="y_ots")
r_ats = m.addVars(arcs, time_steps, scenarios, vtype=GRB.BINARY, name="r_ats")
f_ao = m.addVars(arcs, origins, scenarios, vtype=GRB.CONTINUOUS, name="f_ao")

# Parameters - initialize c_ao correctly
c_ao = {(a, o, s): 0.1 * s for a in arcs for o in origins for s in scenarios}

# Objective Function - Corrected access
objective_expr = quicksum(c_ao[(a, o, s)] * f_ao[a, o, s] for a in arcs for o in origins for s in scenarios)
m.setObjective(objective_expr, GRB.MINIMIZE)

# Constraints
# Flow conservation
for n in nodes:
    for t in time_steps:
        for s in scenarios:
            m.addConstr(
                quicksum(f_ao[(i, n), o, s] for i, n in arcs if (i, n) in arcs for o in origins) ==
                quicksum(f_ao[(n, j), o, s] for n, j in arcs if (n, j) in arcs for o in origins), 
                "flow_conservation_{}_{}_{}".format(n, t, s)
            )

# Capacity constraints
for a in arcs:
    for t in time_steps:
        for s in scenarios:
            m.addConstr(
                quicksum(f_ao[a, o, s] for o in origins) <= q_a[a] * (1 - r_ats[a, t, s]) + 
                quicksum(delta_q_a[a] * z_nts[n, t, s] for n in nodes) + (q_a[a] + delta_q_a[a]) * r_ats[a, t, s],
                "capacity_{}_{}_{}".format(a, t, s)
            )

# Resource deployment limits
for n in nodes:
    for t in time_steps:
        for s in scenarios:
            m.addConstr(z_nts[n, t, s] <= 1, "resource_limit_{}_{}_{}".format(n, t, s))

# Optimize the model
m.optimize()

# Output results
for v in m.getVars():
    if v.x > 0.1:  # Small threshold to ignore essentially zero values
        print(f'{v.varName}: {v.x}')

# Print the objective value
print(f'Objective Value: {m.objVal}')
