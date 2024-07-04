import time
from CVRPSolver.TSP.ACO import ACO
from CVRPSolver.TSP.dijkstra import dp, dijkstra
from CVRPSolver.TSP.brute_force import brute_force


TIMES = {
    1: (8.700000762473791e-07, dijkstra),
    2: (7.18999799573794e-06, brute_force),
    3: (1.2870000500697642e-05, brute_force),
    4: (3.699000008055009e-05, brute_force),
    5: (0.00018925010226666927, brute_force),
    6: (0.000616779999108985, dp),
    7: (0.0015050302004965487, dp),
    8: (0.008828601102140964, dp),
    9: (0.035031454100681, dp),  # TODO: garbage collection triggered during timing?
    10: (0.02357880380077404, dp),
    11: (0.06692541950033046, dp),
    12: (0.14298049889985123, dp),
    13: (0.3345584875998611, dp),
    14: (0.6392210653997609, dp),
}


def reoptimize_routes(sol, end, conf):
    sol.obj = 0
    for car, route in enumerate(sol):
        if len(route) <= 1:
            continue
        if not (time.time() < end):
            sol.obj = sol.objective(recompute=True)
            return sol

        if len(route) <= min(conf["TSP_EXACT_THRESHOLD"], len(TIMES)):
            t, fnc = TIMES[len(route)]
            if end - time.time() < t:
                d, route = fnc(route, sol.dist)
                sol.routes[car] = route
                sol.obj += d
            else:
                sol.obj = sol.objective(recompute=True)
                return sol
        else:
            d, route = ACO(route, sol.dist, time.time() + conf["TSP_TIME_LIMIT"], conf)
            sol.routes[car] = route
            sol.obj += d

    sol.obj += sol.exceeded_capacity_penalty()
    return sol