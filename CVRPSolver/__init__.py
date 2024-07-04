from CVRPSolver.CVRP.CVRP import solve
from CVRPSolver.CVRP.initial import generate_initial_solution
from CVRPSolver.TSP.ACO import ACO as ACO_helper
from CVRPSolver.TSP.dijkstra import dijkstra, dp
from CVRPSolver.TSP.brute_force import brute_force
from CVRPSolver.CVRP.configuration import CONFIG_SPACE, DEFAULT_CONFIG, check_user_configuration

import time


def ACO(route, dist, conf=DEFAULT_CONFIG):
    conf = check_user_configuration(conf)
    return ACO_helper(route, dist, time.time() + conf["TSP_TIME_LIMIT"], conf)


__all__ = [
    "solve",
    "generate_initial_solution",
    "ACO",
    "dijkstra",
    "dp",
    "brute_force",
    "CONFIG_SPACE", 
    "DEFAULT_CONFIG",
]