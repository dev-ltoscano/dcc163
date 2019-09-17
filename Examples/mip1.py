# -*- coding: utf-8 -*-

import gurobipy as grb

try:
    # Create a new model
    m = grb.Model("mip1")

    # Create variables
    x = m.addVar(vtype=grb.GRB.BINARY, name="x")
    y = m.addVar(vtype=grb.GRB.BINARY, name="y")
    z = m.addVar(vtype=grb.GRB.BINARY, name="z")

    # Set objective
    m.setObjective(x + y + 2 * z, grb.GRB.MAXIMIZE)

    # Add constraint: x + 2 y + 3 z <= 4
    m.addConstr(x + 2 * y + 3 * z <= 4, "c0")

    # Add constraint: x + y >= 1
    m.addConstr(x + y >= 1, "c1")

    # Optimize model
    m.optimize()

    for v in m.getVars():
        print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)
    print('Terminated!')
except grb.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))
except AttributeError:
    print('Encountered an attribute error')