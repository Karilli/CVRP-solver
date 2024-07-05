# CVRP Solver
This project provides a solution to the Capacitated Vehicle Routing Problem (CVRP) using a variety of optimization techniques, including Variable Neighborhood Search (VNS), Traveling Salesman Problem (TSP) solvers, Dijkstra-like algorithms, and Ant Colony Optimization (ACO).

# Capacitated Vehicle Routing Problem (CVRP)
The Capacitated Vehicle Routing Problem (CVRP) is a well-known combinatorial optimization problem where the objective is to determine the optimal set of routes for a fleet of vehicles to deliver goods to a set of customers, subject to capacity constraints. (This solver assumes that all vehicles have the same capacity)

# Approach
The CVRP solver uses a hierarchical approach to efficiently solve the problem by leveraging different optimization techniques based on the problem size:
1. Variable Neighborhood Search (VNS):
 - The primary method used to solve the CVRP.
 - Executes another instance of VNS with a limited number of destroy/repair iterations on the current solution. If this smaller VNS does not achieve an improvement within the given iteration budget, the VNS solver reverts to the original version of the current solution prior to its modification by the smaller VNS. (This is probably some combination of acceptance and VNS)
2. Solving Individual Routes:
 - For smaller sub-problems (i.e., individual routes within the CVRP), the solver uses specialized TSP solvers.
  - Dijkstra-like Algorithm and Dynamic Programming (DP): Used for very small TSP instances.
  - Ant Colony Optimization (ACO): For larger TSP instances.

# HPO and configuration
The hyper-parameters are optimized using script in [hpo.py](hpo.py) and [amltk](https://automl.github.io/amltk/latest/) for instances in [data](data) folder and the best configurations are stored in lists LARGE_CONFIGS and SMALL_CONFIGS (checkout [usage.ipynb](usage.ipynb) for more information). You can configure the solver by passing arguments via `conf` parameter of function `solver` or by providing additional parameter in terminal. 

# Usage
To learn the python API, look into the [usage.ipynb](usage.ipynb). You can also use the solver from terminal. I strongly suggest using different interpreter then python, to make the solver faster.
```
$ pypy CVRP.solver/main.py <your-instance.json> <your-output.json>               # run the solver from terminal
$ pypy CVRP.solver/main.py <your-instance.json> <your-output.json> <your-config> # you can add a configuration
$ pypy ./data/cvrp_32.json ./out.json {TIME_LIMIT:30,SEED:0}                     # concrete example
```
- `your-instance.json` json file containing information about the problem, you can see the required fields in instances in `data`
- `your-output.json` path to the output file, the file does not have to exist, but the directories leading to it must exist.
- `your-config` a python-like dictionary without any white-spaces and quotas, look into [CVRPSolver.CVRP.CVRP.configuration](CVRPSolver.CVRP.CVRP.configuration) for more information on the `configuration space`
> [!TIP]
> Running the solver for more then few minutes (around 5 minutes using pypy) is probably a waste of time, trying other configurations, or the same configuration with different seeds, instead should lead to better outcome.
> Checkout LARGE_CONFIGS and SMALL_CONFIGS for other performent configurations.
> Try runnig a few solver instances in parallel. (You will have to implement it yourself)
