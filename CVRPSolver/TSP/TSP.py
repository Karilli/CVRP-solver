import time
from CVRPSolver.TSP.ACO import ACO
from CVRPSolver.TSP.dijkstra import dp, dijkstra
from CVRPSolver.TSP.brute_force import brute_force


TIMES = {
    1: (1.040839997585863e-05, dijkstra),
    2: (2.7430000045569614e-05, brute_force),
    3: (3.4174399843323044e-05, brute_force),
    4: (5.309839980327524e-05, brute_force),
    5: (0.00015289879956981167, dp),
    6: (0.0003109343997493852, dp),
    7: (0.0007205426005384652, dp),
    8: (0.001640589399903547, dp),
    9: (0.0050190899994049685, dp),
    10: (0.010968710000088321, dp),
    11: (0.02409385739993013, dp),
    12: (0.07534630459995242, dp),
    13: (0.14743490899963946, dp),
    14: (0.37331541080056924, dp),
    15: (0.8144068609999522, dp),
    16: (1.9742409139998927, dp),
    17: (4.418484903799981, dp),
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