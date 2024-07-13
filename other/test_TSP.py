##############################################
import sys, os                              ##
sys.path.insert(0, os.path.abspath("."))    ##
##############################################

import random 
from math import inf
from itertools import permutations
from CVRPSolver import brute_force, ACO, dijkstra, dp


EPS = 1e-5
TSP_CONFIG = {
    "TSP_TIME_LIMIT": 15,
    "TSP_ALPHA": 3,
    "TSP_BETA": 3,
    "TSP_EVAPORATION": 0.3,
    "TSP_ANTS": 100,
    "TSP_INITIAL_PHEROMONE": 1,
}


def route_distance(route, dist):
    route = tuple(route)
    return sum(dist[a][b] for a, b in zip((0,) + route, route + (0,)))


def best_routes(route, dist):
    mn, routes = inf, set()
    for perm in permutations(route):
        d = route_distance(perm, dist)
        
        if abs(d - mn) < EPS:
            routes.add(perm)
        elif d < mn:
            mn, routes = d, {perm}
    return mn, routes


def check(d, path, best, routes, dist):
    x = route_distance(path, dist)
    assert abs(best - d) < EPS, f"{best}, {d}, {path}"
    assert abs(best - x) < EPS, f"{best}, {x}, {path}"
    assert abs(x - d) < EPS, f"{x}, {d}, {path}"
    assert tuple(path) in routes or tuple(path[::-1]) in routes, f"{path}, {routes}"


def random_problem(size):
    from math import dist
    locations = [(random.randint(0, 20), random.randint(0, 20)) for _ in range(size)]
    n = len(locations)
    mat = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            mat[i][j] = round(dist(locations[i], locations[j]), 2)
    return locations, mat


def check_all(route, dist):
    best, routes = best_routes(route, dist)
    check(*dijkstra(route, dist), best, routes, dist)
    check(*brute_force(route, dist), best, routes, dist)
    check(*dp(route, dist), best, routes, dist)
    try:
        check(*ACO(route, dist, TSP_CONFIG), best, routes, dist)
    except:
        pass
    try:
        check(*ACO(route, dist, TSP_CONFIG), best, routes, dist)
    except:
        pass
    try:
        check(*ACO(route, dist, TSP_CONFIG), best, routes, dist)
    except AssertionError as e:
        a, b, *_ = str(e).split(", ")
        if not (0.9 < float(a) / float(b) < 1.111):  # NOTE: ACO does not solve the problem exactly, so it can fail sometimes ...
            raise e


def main():
    route = [1, 2, 3]
    dist = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]
    check_all(route, dist)

##########################

    route = [1, 2, 3]
    dist = [
        [0.00,  4.12,  11.66, 11.18],
        [4.12,  0.00,  15.65, 13.42],
        [11.66, 15.65, 0.00,  9.43],
        [11.18, 13.42, 9.43,  0.00]
    ]
    check_all(route, dist)

##########################

    locations, dist = random_problem(100)
    for i in range(1, 11):
        route = random.sample(list(range(1, len(locations))), k=i)
        assert len(route) == len(set(route))
        check_all(route, dist)


if __name__ == "__main__":
    main()
