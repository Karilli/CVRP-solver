from math import inf, dist
from functools import partial
import random


class Tabu:
    Q = []
    len = 0
    idx = 0

    @classmethod
    def init(cls, length):
        cls.len = length
        cls.Q = [-1] * cls.len
        cls.idx = 0

    @classmethod
    def add(cls, location):
        cls.Q[cls.idx] = location
        cls.idx = (cls.idx + 1) % cls.len

    @classmethod
    def contains(cls, elem):
        return elem in cls.Q


def destroy_shaw_removal(sol, destroy_heuristic):   
    _, _, loc = destroy_heuristic(sol)
    _, car2, idx2, loc2 = min(
        (sol.dist[loc][loc2], car2, idx2, loc2) 
        for car2, route2 in enumerate(sol) 
        for idx2, loc2 in enumerate(route2) 
        if not Tabu.contains(loc2)
    )
    Tabu.add(loc2)
    sol.remove(car2, idx2)


def destroy_worst(sol):
    _, car, idx, loc = min(
        (sol.incremental_remove(car, idx), car, idx, loc) 
        for car, route in enumerate(sol) 
        for idx, loc in enumerate(route) 
        if not Tabu.contains(loc)
    )
    Tabu.add(loc)
    sol.remove(car, idx)
    return car, idx, loc


def destroy_random_route(sol):
    car, route = random.choice(list(enumerate(sol)))
    for _ in range(len(route)):
        sol.remove(car, 0)
    return car


def destroy_shaw_removal_route(sol):
    def centroid(route):
        x, y = 0, 0
        if not route:
            return x, y
        for loc in route:
            x += sol.locations[loc][0]
            y += sol.locations[loc][1]
        return x/len(route), y/len(route)

    centroids = [centroid(route) for route in sol]
    car = destroy_random_route(sol)
    _, car2, route2 = min(
        (dist(centroids[car], centroids[car2]), car2, route2)
        for car2, route2 in enumerate(sol)
        if car != car2
    )
    for _ in range(len(route2)):
        sol.remove(car2, 0)


def destroy_random(sol):
    car, idx, loc = random.choice([
        (car, idx, loc) 
        for car, route in enumerate(sol) 
        for idx, loc in enumerate(route) 
        if not Tabu.contains(loc)
    ])
    Tabu.add(loc)
    sol.remove(car, idx)
    return car, idx, loc


def do_intersect(p1x, p1y, q1x, q1y, p2x, p2y, q2x, q2y):
    # def on_segment(px, py, qx, qy, rx, ry):
    #     return all((
    #         min(px, rx) <= qx <= max(px, rx),
    #         min(py, ry) <= qy <= max(py, ry),
    #     ))

    def orientation(px, py, qx, qy, rx, ry):
        x = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
        if x == 0:
            return 0
        return abs(x) / x

    o1 = orientation(p1x, p1y, q1x, q1y, p2x, p2y)
    o2 = orientation(p1x, p1y, q1x, q1y, q2x, q2y)
    o3 = orientation(p2x, p2y, q2x, q2y, p1x, p1y)
    o4 = orientation(p2x, p2y, q2x, q2y, q1x, q1y)

    return o1 != o2 and o3 != o4
    # return any((
    #     o1 != o2 and o3 != o4, 
    #     o1 == 0 and on_segment(p1x, p1y, p2x, p2y, q1x, q1y),
    #     o2 == 0 and on_segment(p1x, p1y, q2x, q2y, q1x, q1y),
    #     o3 == 0 and on_segment(p2x, p2y, p1x, p1y, q2x, q2y),
    #     o4 == 0 and on_segment(p2x, p2y, q1x, q1y, q2x, q2y),
    # ))


def destroy_crossed_lines(sol):
    a = [
        (car, max(0, idx-1), loc1, loc2)
        for car, route in enumerate(sol)
        for idx, (loc1, loc2) in enumerate(zip([0] + route, route + [0]))
        if route
    ]
    random.shuffle(a)
    for i, (car1, idx1, loc11, loc12) in enumerate(a):
        for car2, idx2, loc21, loc22 in a[i+1:]:
            if len({loc11, loc12, loc21, loc22}) == 4 and do_intersect(
                *sol.locations[loc11],
                *sol.locations[loc12],
                *sol.locations[loc21],
                *sol.locations[loc22],
            ):
                lst = [(idx1, car1), (idx2, car2)]
                if not (loc11 == 0 or loc12 == 0):
                    lst.append((idx1+1, car1))
                if not (loc21 == 0 or loc22 == 0):
                    lst.append((idx2+1, car2))
                for idx, car in sorted(lst, reverse=True):
                    sol.remove(car, idx)
                return


def repair_regret(sol, max_k):
    mn1, i1, j1 = inf, -1, -1
    mn2, i2, j2 = inf, -1, -1
    res = []
    for loc in random.sample(list(sol.unassigned), k=min(len(sol.unassigned), max_k)):
        for car, route in enumerate(sol):
            for idx in range(len(route) + 1):
                new_obj = sol.incremental_add(car, idx, loc)
                if new_obj < mn2:
                    mn2, i2, j2 = new_obj, car, idx
                    (mn1, i1, j1), (mn2, i2, j2) = sorted(((mn1, i1, j1), (mn2, i2, j2)))
        res.append((mn2 - mn1, i1, j1, loc))

    _, i, j, k = max(res)
    sol.add(i, j, k)


def repair_best(sol, max_k):
    _, car, idx, loc = min(
        (sol.incremental_add(car, idx, loc), car, idx, loc)
        for loc in random.sample(list(sol.unassigned), k=min(len(sol.unassigned), max_k))
        for car, route in enumerate(sol)
        for idx in range(len(route) + 1)
    )
    sol.add(car, idx, loc)


def repair_best_2(sol, max_k):
    def possible_adds():
        for loc in random.sample(list(sol.unassigned), k=min(len(sol.unassigned), max_k)):
            for car, route in enumerate(sol):
                for idx in range(len(route) + 1):
                    yield car, idx, loc

    if len(sol.unassigned) == 1:
        return repair_best(sol, max_k)

    mn, car1_, idx1_, loc1_, car2_, idx2_, loc2_ = inf, None, None, None, None, None, None

    for car1, idx1, loc1 in possible_adds():
        sol.add(car1, idx1, loc1)
        for car2, idx2, loc2 in possible_adds():
            obj = sol.incremental_add(car2, idx2, loc2)
            if obj < mn:
                mn, car1_, idx1_, loc1_, car2_, idx2_, loc2_ = obj, car1, idx1, loc1, car2, idx2, loc2
        sol.remove(car1, idx1)

    sol.add(car1_, idx1_, loc1_)
    sol.add(car2_, idx2_, loc2_)


def repair_farthest(sol, max_k=None):
    _, loc = max((sol.dist[0][loc], loc) for loc in sol.unassigned)
    _, car, idx, loc = min(
        (sol.incremental_add(car, idx, loc), car, idx, loc)
        for car, route in enumerate(sol)
        for idx in range(len(route) + 1)
    )
    sol.add(car, idx, loc)


def repair_random(sol, max_k=None):
    loc = random.choice(list(sol.unassigned))
    car, idx = random.choice([
        (car, idx)
        for car, route in enumerate(sol) 
        for idx in range(len(route) + 1)
    ])
    sol.add(car, idx, loc)


destroy_shaw_worst = partial(destroy_shaw_removal, destroy_heuristic=destroy_worst)
destroy_shaw_random = partial(destroy_shaw_removal, destroy_heuristic=destroy_random)
