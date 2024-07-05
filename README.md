# CVRP Solver
This project provides a solution to the Capacitated Vehicle Routing Problem (CVRP) using a variety of optimization techniques, including Variable Neighborhood Search (VNS), Traveling Salesman Problem (TSP) solvers, Dijkstra-like algorithms, and Ant Colony Optimization (ACO). It is written in pure python.

# CVRP
The Capacitated Vehicle Routing Problem (CVRP) is a well-known combinatorial optimization problem where the objective is to determine the optimal set of routes for a fleet of vehicles to deliver goods to a set of customers, subject to capacity constraints. (This solver assumes that all vehicles have the same capacity)

# Approach
The CVRP solver uses a hierarchical approach to efficiently solve the problem by leveraging different optimization techniques based on the problem size:
1. Variable Neighborhood Search (VNS):
  - The primary method used to solve the CVRP.
  - It creates a copy of the best solution, which is then optimized through a set number of destroy/repair iterations. If a better solution is found
  within this iteration budget, the new solution is accepted; otherwise, it is discarded. In either case, the budget is then reset.
2. Solving Individual Routes:
  - For smaller sub-problems (i.e., individual routes within the CVRP), the solver uses specialized TSP solvers.
    - Dijkstra-like Algorithm and Dynamic Programming (DP): Used for very small TSP instances.
    - Ant Colony Optimization (ACO): For larger TSP instances.
> [!NOTE]
> For more in-depth understanding of the solver, look into `showcase.ipynb` or the source code of `CVRPSolver`.

# HPO and configuration
The hyper-parameters are optimized using script in [hpo.py](hpo.py) and [amltk](https://automl.github.io/amltk/latest/) for instances in [data](data) folder. The best configurations are stored in lists LARGE_CONFIGS and SMALL_CONFIGS, sorted by their performance on instances in `data`, with the best configurations at the beginning of the lists (see [usage.ipynb](usage.ipynb) for more information). 

# Usage
To learn the python API, look into the [usage.ipynb](usage.ipynb). You can also use the solver from terminal. I strongly suggest using different interpreter then python, to make the solver faster.
```
$ pypy3 ./main.py <your-instance.json> <your-output.json>                         # run the solver from terminal
$ pypy3 ./main.py <your-instance.json> <your-output.json> <your-config>           # you can add a configuration
$ pypy3 ./main.py ./data/cvrp_32.json ./out.json '{"TIME_LIMIT":30, "SEED":0}'    # concrete example - make sure to pass config as 1 argument
$ pypy3 ./main.py ./data/cvrp_32.json ./out.json '{"TIME_LIMIT" : 30, SEED:"0"}'  # quotas around values and white-spaces are ignored
```
- `your-instance.json` json file containing information about the problem, you can see the required fields in instances in `data`
- `your-output.json` path to the output file, the file does not have to exist, but the directories leading to it must exist.
- `your-config` a python-like dictionary - all white spaces and quotas will be removed, but make sure to pass the "dict" as one parameter, look into [CVRPSolver.CVRP.CVRP.configuration](CVRPSolver.CVRP.CVRP.configuration) for more information on the `configuration space`
> [!TIP]
> Running the solver for more then few minutes (around 5 minutes using pypy) is probably a waste of time, trying other configurations, or the same configuration with different seeds, instead should lead to better outcome.
> Checkout LARGE_CONFIGS and SMALL_CONFIGS for other performent configurations.
> Try runnig a few solver instances in parallel.

# Ideas for future
* learn neural network as destroy/repair heuristic
* repair heuristic, that does not take into a count the second route to depot
* start with random subset of locations, optimize it, iteratively add a few random locations 
  * dont start with random subset, but with locations nearest to depot
* repair heuristic that starts with the smallest route and adds the best locations until the capacity is exhausted
* try destroy route heuristics with lower probability
  * or dont destroy the whole route
  * choose only destroy route heuristics or only other destroy heuristics
* introduce initial heuristics probability again?
* alternative acceptance methods