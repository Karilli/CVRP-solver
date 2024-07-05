##############################################
import sys, os                              ##
sys.path.insert(0, os.path.abspath("."))    ##
##############################################

from CVRPSolver.TSP.dijkstra import Memo
from CVRPSolver import brute_force, dijkstra, dp
from test_TSP import random_problem
from time import perf_counter
from math import inf
import random


N = 10
MAX = 15


def main():
    locations, dist = random_problem(100)
    Memo.resize(MAX)

    for i in range(1, MAX):
        res = {}
        for f in dp, dijkstra, brute_force:
            total = 0
            if 10 < i and f is brute_force:
                res[f] = inf
                continue
            for _ in range(N):      
                route = random.sample(list(range(1, len(locations))), k=i)
                t = perf_counter()
                f(route, dist)
                total += perf_counter() - t
            res[f] = total / N

        t, _, f = min((res[f], j, str(f).split()[1]) for j, f in enumerate((dp, dijkstra, brute_force)))
        x = "'"
        print(f"{i}: ({t}, {f.replace(x, '')})")


if __name__ == "__main__":
    main()
