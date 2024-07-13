from itertools import permutations

def brute_force(route, dist):
    def route_distance(route):
        return sum(dist[a][b] for a, b in zip(route, route[1:])) + dist[0][route[0]] + dist[route[-1]][0]

    d, res = min((route_distance(perm), perm) for perm in permutations(route))
    return d, list(res)
