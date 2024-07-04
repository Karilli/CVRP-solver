from itertools import permutations

def brute_force(route, dist):
    def route_distance(route, dist):
        return sum(dist[a][b] for a, b in zip((0,) + route, route + (0,)))

    d, res = min((route_distance(perm, dist), perm) for perm in permutations(route))
    return d, list(res)
