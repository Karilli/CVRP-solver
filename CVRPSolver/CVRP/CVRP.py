import time
import random
from functools import partial
from collections import Counter

from CVRPSolver.CVRP.heuristics import (
    Tabu,
    destroy_worst,
    destroy_random,
    destroy_shaw_worst, 
    destroy_shaw_random,
    repair_best,
    # repair_random,
    repair_regret,
    repair_farthest,
    # destroy_shaw_removal_route,
    # destroy_random_route,
)
from CVRPSolver.CVRP.configuration import check_user_configuration
from CVRPSolver.CVRP.initial import generate_initial_solution
from CVRPSolver.CVRP.representation import Solution
from CVRPSolver.TSP.TSP import reoptimize_routes
from CVRPSolver.TSP.dijkstra import Memo


DESTROY_HEURISTICS = [
    destroy_worst,
    destroy_random,
    destroy_shaw_worst, 
    destroy_shaw_random,
    # destroy_random_route,  # NOTE: bad heuristic
    # destroy_shaw_removal_route,  # NOTE: bad heuristic
]

REPAIR_HEURISTICS = [
    repair_best,
    # repair_random,  # NOTE: bad heuristic
    repair_regret,
    repair_farthest
]


def solve(dist, locations, demands, N, C, conf={}):
    def help(seed, end):
        random.seed(seed)

        misses = Counter()
        for h in DESTROY_HEURISTICS + REPAIR_HEURISTICS:
            misses[h] = conf["VNS_MISSSES_INIT"]

        best = sol = generate_initial_solution(dist, locations, demands, N, C, conf["INITIAL_STRATEGY"], T=conf["GREEDY_ALL_ROUTES_RANDOMIZED_T"])
        while time.time() < end:
            new_sol = VNS(sol, misses, conf, end)
            if random.random() < conf["REOPTIMIZE_CHANCE"]:
                reoptimize_routes(new_sol, end, conf)
            if new_sol.objective() < sol.objective():
                sol = new_sol
                if new_sol.is_feasible() and new_sol < best:
                    best = new_sol
        return best

    # NOTE: first try is responsible for initialization and therefore has less time then other tries
    start = time.time()
    conf = check_user_configuration(conf)
    random.seed(conf["SEED"])
    Tabu.init(min(conf["TABU_LEN"], len(demands) - 3))
    Solution.CAPACITY_PENALTY = conf["CAPACITY_PENALTY"]
    Memo.resize(conf["TSP_EXACT_THRESHOLD"])
    seeds = [random.randint(0, 10**6) for _ in range(conf["TRIES"])]
    ends = [start + i * conf["TIME_LIMIT"] / conf["TRIES"] for i in range(1, conf["TRIES"] + 1)]
    return min(help(seed, end) for seed, end in zip(seeds, ends))


def VNS(sol, misses, conf, end):
    new_sol = sol.copy()
    it = 0
    while not (new_sol < sol) and it < conf["VNS_MAX_ITERATIONS"] and time.time() < end:
        it += 1
        history = Counter()
        while len(new_sol.unassigned) < len(new_sol.demands) * conf["DESTROY_DEGREE"] and time.time() < end:
            destroy_heuristic = random.choices(DESTROY_HEURISTICS, [1/misses[h] for h in DESTROY_HEURISTICS])[0]
            destroy_heuristic(new_sol)
            history[destroy_heuristic] += 1
        while new_sol.unassigned and time.time() < end:
            repair_heuristic = random.choices(REPAIR_HEURISTICS, [1/misses[h] for h in REPAIR_HEURISTICS])[0]
            repair_heuristic(new_sol, max_k=conf["REPAIR_MAX_K"])
            history[repair_heuristic] += 1
        if not (new_sol < sol):
            for h, c in history.items():
                misses[h] += c
    return new_sol
