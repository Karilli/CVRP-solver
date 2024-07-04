from CVRPSolver.CVRP.configuration import DEFAULT_CONFIG
import random, time


EPS = 10**(-5)


class Pheromones:
    def __init__(self, nodes, initial):
        self.pheromones = [[1] * nodes for _ in range(nodes)]
        self.delta = [[0] * nodes for _ in range(nodes)]
        for a, b in zip(range(nodes), range(1, nodes)):
            self.pheromones[a][b] = self.pheromones[b][a] = initial
        self.pheromones[nodes - 1][0] = self.pheromones[0][nodes - 1] = initial
    
    def evaporate(self, evaporation):
        for i in range(len(self.pheromones)):
            for j in range(i + 1, len(self.pheromones)):
                delta = self.delta[i][j] + self.delta[j][i]
                self.pheromones[i][j] = self.pheromones[j][i] = (1 - evaporation) * self.pheromones[i][j] + delta
                self.delta[i][j] = self.delta[j][i] = 0
    
    def ant_update(self, path, traveled_distance):
        for a, b in zip(path, path[1:] + [path[0]]):
            self.delta[a][b] += 1 / traveled_distance
    
    def __getitem__(self, idx):
        return self.pheromones[idx]


def ACO(route, dist, end, conf=DEFAULT_CONFIG):
    def distance(i, j):
        i = 0 if i == 0 else route[i - 1]
        j = 0 if j == 0 else route[j - 1]
        return dist[i][j]

    def path_distance(path):
        return sum(distance(a, b) for a, b in zip(path, path[1:])) + distance(path[0], path[-1])

    def edge_prob(i, j, visited):
        if visited[j]:
            return 0
        return pow(pheromones[i][j], conf["TSP_ALPHA"]) * pow(distance(i, j) + EPS, -conf["TSP_BETA"])
    
    def extract_route(path):
        j = path.index(0)
        return [0 if i == 0 else route[i - 1] for i in path[j + 1 :] + path[:j]]

    def walk_ant():
        i = random.randint(0, N - 1)
        path, visited = [i], [False] * N
        visited[i] = True
        while len(path) != N:
            i = random.choices(range(N), [edge_prob(path[-1], j, visited) for j in range(N)])[0]
            path.append(i)
            visited[i] = True

        curr_dist = path_distance(path)
        pheromones.ant_update(path, curr_dist)

        return curr_dist, path

    N = len(route) + 1
    pheromones = Pheromones(N, conf["TSP_INITIAL_PHEROMONE"])

    best = list(range(N))
    best_obj = path_distance(best)

    found = True
    while found:
        found = False
        for _ in range(conf["TSP_ANTS"]):
            if not (time.time() < end):
                return best_obj, extract_route(best)
            walked_dist, path = walk_ant()
            if walked_dist < best_obj:
                found = True
                best_obj = walked_dist
                best = path
        pheromones.evaporate(conf["TSP_EVAPORATION"])
    return best_obj, extract_route(best)
