from heapq import heapify, heappop
from math import inf

import random

from CVRPSolver.CVRP.representation import Solution


def rand(dist, locations, demands, N, C):
    M = len(demands)

    perm = [i for i in range(1, N + M)]
    random.shuffle(perm)

    routes = [[]]
    for a in perm:
        if a < M:
            routes[-1].append(a)
        else:
            routes.append([])

    capacities = [sum(demands[location] for location in row) for row in routes]
    exceeded_capacity = {i for i, capacity in enumerate(capacities) if not capacity <= C}
    return Solution(routes, capacities, set(), exceeded_capacity, dist, locations, demands, C)


# def greedy_all_routes_slow(dist, locations, demands, N, C):
#     routes = [[] for _ in range(N)]
#     capacity = [0] * N
#     unassigned = set(range(1, len(demands)))

#     for _ in range(1, len(demands)):
#         mn = inf
#         i, j = 0, 0
#         for location in unassigned:
#             for car in range(N):
#                 a = routes[car][-1] if routes[car] else 0
#                 b = location
#                 if dist[a][b] < mn and capacity[car] + demands[location] <= C:
#                     mn, i, j = dist[a][b], car, location

#         unassigned.remove(j)
#         capacity[i] += demands[j]
#         routes[i].append(j)

#     return Solution(routes, capacity, unassigned, {car for car in range(N) if not (capacity[car] <= C)}, dist, locations, demands, C)


def greedy_all_routes(dist, locations, demands, N, C):
    M = len(demands)
    routes = [[] for _ in range(N)]
    capacity = [0] * N
    unassigned = {i for i in range(1, M)}

    nearest_unassigned_locations = [[(dist[a][b], b) for b in range(1, M)] for a in range(M)]
    for row in nearest_unassigned_locations:
        heapify(row)

    while unassigned:
        mn1, i1, j1 = inf, inf, inf
        mn2, i2, j2 = inf, inf, inf
        for car in range(N):
            a = routes[car][-1] if routes[car] else 0
            while True:
                _, b = nearest_unassigned_locations[a][0]
                if b in unassigned:
                    break
                heappop(nearest_unassigned_locations[a])

            if dist[a][b] < mn1 and capacity[car] + demands[b] <= C:
                mn1, i1, j1 = dist[a][b], car, b
            if dist[a][b] < mn2:
                mn2, i2, j2 = dist[a][b], car, b

        if mn1 != inf:
            unassigned.remove(j1)
            capacity[i1] += demands[j1]
            routes[i1].append(j1)
        else:
            unassigned.remove(j2)
            capacity[i2] += demands[j2]
            routes[i2].append(j2)
    return Solution(routes, capacity, unassigned, {car for car in range(N) if not (capacity[car] <= C)}, dist, locations, demands, C)


def greedy_all_routes_randomized(dist, locations, demands, N, C, T=2):
    mx = max(d for row in dist for d in row)
    rescaled_dist = [[d / mx + 1e-1 for d in row] for row in dist]

    M = len(demands)
    routes = [[] for _ in range(N)]
    capacity = [0] * N
    unassigned = {i for i in range(1, M)}

    while unassigned:
        mn1, i1, j1 = inf, inf, inf
        mn2, i2, j2 = inf, inf, inf
        nxt = [b for b in range(1, M) if b in unassigned]
        for car in range(N):
            a = routes[car][-1] if routes[car] else 0
            b = random.choices(nxt, [2.7**(T/(rescaled_dist[a][b])) for b in nxt])[0]

            if dist[a][b] < mn1 and capacity[car] + demands[b] <= C:
                mn1, i1, j1 = dist[a][b], car, b
            if dist[a][b] < mn2:
                mn2, i2, j2 = dist[a][b], car, b

        if mn1 != inf:
            unassigned.remove(j1)
            capacity[i1] += demands[j1]
            routes[i1].append(j1)
        else:
            unassigned.remove(j2)
            capacity[i2] += demands[j2]
            routes[i2].append(j2)
    return Solution(routes, capacity, unassigned, {car for car in range(N) if not (capacity[car] <= C)}, dist, locations, demands, C)


def greedy_all_routes_start_at_random_location(dist, locations, demands, N, C):
    M = len(demands)
    routes = [[loc] for loc in random.sample(range(1, M), k=N)]
    capacity = [demands[route[0]] for route in routes]
    unassigned = {i for i in range(1, M)} - {route[0] for route in routes}

    nearest_unassigned_locations = [[(dist[a][b], b) for b in range(1, M)] for a in range(M)]
    for row in nearest_unassigned_locations:
        heapify(row)

    while unassigned:
        mn1, i1, j1 = inf, inf, inf
        mn2, i2, j2 = inf, inf, inf
        for car in range(N):
            a = routes[car][-1]
            while True:
                _, b = nearest_unassigned_locations[a][0]
                if b in unassigned:
                    break
                heappop(nearest_unassigned_locations[a])

            if dist[a][b] < mn1 and capacity[car] + demands[b] <= C:
                mn1, i1, j1 = dist[a][b], car, b
            if dist[a][b] < mn2:
                mn2, i2, j2 = dist[a][b], car, b

        if mn1 != inf:
            unassigned.remove(j1)
            capacity[i1] += demands[j1]
            routes[i1].append(j1)
        else:
            unassigned.remove(j2)
            capacity[i2] += demands[j2]
            routes[i2].append(j2)
    return Solution(routes, capacity, unassigned, {car for car in range(N) if not (capacity[car] <= C)}, dist, locations, demands, C)


def greedy_equal_loads(dist, locations, demands, N, C):
    M = len(demands)
    routes = [[] for _ in range(N)]
    capacity = [0] * N
    unassigned = {i for i in range(1, M)}

    nearest_unassigned_locations = [[(dist[a][b], b) for b in range(1, M)] for a in range(M)]
    for row in nearest_unassigned_locations:
        heapify(row)

    factor = 0.75
    while True:
        while True:
            options = sorted((car for car in range(N) if capacity[car] < factor * C), key=lambda car: capacity[car],)
            if options:
                break
            factor += 0.1

        for car in options:
            if not unassigned:
                return Solution(routes, capacity, unassigned, {car for car in range(N) if not (capacity[car] <= C)}, dist, locations, demands, C)
            a = routes[car][-1] if routes[car] else 0
            while True:
                _, b = nearest_unassigned_locations[a][0]
                if b in unassigned:
                    break
                heappop(nearest_unassigned_locations[a])

            unassigned.remove(b)
            capacity[car] += demands[b]
            routes[car].append(b)


def clark_and_wright_savings(dist, locations, demands, N, C):
    def merge_savings(car1, car2, a, b):
        if not routes[car1] or not routes[car2] or car1 == car2:
            return -inf
        if not (capacity[car1] + capacity[car2] <= C):
            return -inf
        return dist[loc1][routes[car1][a]] - dist[0][loc1] - dist[routes[car2][b]][0]

    def merge(car1, car2, a, b):
        if not routes[car1] or not routes[car2] or car1 == car2:
            return
        if not (capacity[car1] + capacity[car2] <= C):
            return
        for loc in routes[car2]:
            assignment[loc] = car1
        if a == 0:
            routes[car1].reverse()
        if b == -1:
            routes[car2].reverse()
        routes[car1] += routes[car2]
        routes[car2] = []
        capacity[car1] += capacity[car2]
        capacity[car2] = 0

    M = len(demands)
    routes = [[loc] for loc in range(M)]
    assignment = [loc for loc in range(M)]
    capacity = [demands[loc] for loc in range(M)]

    for loc1 in sorted(range(1, M), key=lambda i: -dist[i][0]):
        car1 = assignment[loc1]
        while True:
            max_savings, i, j, a, b = -inf, inf, inf, inf, inf
            for car2 in range(1, M):
                for c, d in (0, 0), (0, -1), (-1, 0), (-1, -1):
                    max_savings, i, j, a, b = max(
                        (max_savings, i, j, a, b), 
                        (merge_savings(car1, car2, c, d), car1, car2, c, d), 
                    )
            if max_savings == -inf:
                break
            merge(i, j, a, b) 

    new_routes = [[]] * N
    new_capacity = [0] * N
    unassigned = set(range(1, M))
    i = 0
    for route, cap in zip(routes[1:], capacity[1:]):
        for loc in route:
            unassigned.remove(loc)
        if route:
            new_routes[i] = route
            new_capacity[i] = cap
            i += 1
            if i == N:
                break
        
    return Solution(new_routes, new_capacity, unassigned, {car for car in range(N) if not (new_capacity[car] <= C)}, dist, locations, demands, C)


def greedy_one_route(dist, locations, demands, N, C):
    M = len(demands)
    routes = []
    capacity = [] 
    unassigned = {i for i in range(1, M)}

    while unassigned and len(routes) < N-1:
        car = len(routes)
        routes.append([])
        capacity.append(0)
        while unassigned:
            a = routes[car][-1] if routes[car] else 0
            _, b = min((dist[a][b], b) for b in unassigned)
            if not (capacity[car] + demands[b] <= C):
                break
            unassigned.remove(b)
            routes[car].append(b)
            capacity[car] += demands[b]

    new_routes = [[]] * N
    new_capacity = [0] * N
    i = 0
    for route, cap in zip(routes, capacity):
        if route:
            new_routes[i] = route
            new_capacity[i] = cap
            i += 1
            if i == N:
                break
    
    return Solution(new_routes, new_capacity, unassigned, {car for car in range(N) if not (new_capacity[car] <= C)}, dist, locations, demands, C)


def greedy_one_route_start_at_furthest_location(dist, locations, demands, N, C):
    M = len(demands)
    routes = []
    capacity = [] 
    unassigned = {i for i in range(1, M)}

    while unassigned and len(routes) < N-1:
        car = len(routes)
        routes.append([max((dist[0][b], b) for b in unassigned)[1]])
        capacity.append(demands[routes[-1][-1]])
        unassigned.remove(routes[-1][-1])
        while unassigned:
            a = routes[car][-1] if routes[car] else 0
            _, b = min((dist[a][b], b) for b in unassigned)
            if not (capacity[car] + demands[b] <= C):
                break
            unassigned.remove(b)
            routes[car].append(b)
            capacity[car] += demands[b]

    new_routes = [[]] * N
    new_capacity = [0] * N
    i = 0
    for route, cap in zip(routes, capacity):
        if route:
            new_routes[i] = route
            new_capacity[i] = cap
            i += 1
            if i == N:
                break
    
    return Solution(new_routes, new_capacity, unassigned, {car for car in range(N) if not (new_capacity[car] <= C)}, dist, locations, demands, C)


def empty(dist, locations, demands, N, C):
    return Solution([[] for _ in range(N)], [0]*N, {i for i in range(len(demands))}, set(), dist, locations, demands, C)


# TODO: START_AT algos should consider expanding route at the front and at the end
# TODO: MAKE randomized version, where the probability of expanding to a new location
#       is proportional to the lenght of the path
# TODO: parametrize with TEMPERATURE, FACTOR, FACTOR_INCREMENT
def generate_initial_solution(dist, locations, demands, N, C, strategy, **args):
    # if strategy == "GREEDY_ALL_ROUTES_SLOW":  # NOTE: GREEDY_ALL_ROUTES is the same algo, but faster
    #     return greedy_all_routes_slow(dist, locations, demands, N, C)
    if strategy == "GREEDY_ALL_ROUTES":
        return greedy_all_routes(dist, locations, demands, N, C)
    if strategy == "GREEDY_ALL_ROUTES_RANDOMIZED":
        return greedy_all_routes_randomized(dist, locations, demands, N, C, **args)
    if strategy == "GREEDY_ONE_ROUTE":
        return greedy_one_route(dist, locations, demands, N, C)
    if strategy == "GREEDY_ONE_ROUTE_START_AT_FURTHEST_LOCATION":
        return greedy_one_route_start_at_furthest_location(dist, locations, demands, N, C)
    if strategy == "GREEDY_ALL_ROUTES_START_AT_RANDOM_LOCATION":
        return greedy_all_routes_start_at_random_location(dist, locations, demands, N, C)
    if strategy == "CLARK_WRIGTH_SAVINGS":
        return clark_and_wright_savings(dist, locations, demands, N, C)
    if strategy == "EQUAL_LOADS":
        return greedy_equal_loads(dist, locations, demands, N, C)
    if strategy == "RANDOM":
        return rand(dist, locations, demands, N, C)
    if strategy == "EMPTY":
        return empty(dist, locations, demands, N, C)
    assert False, strategy
