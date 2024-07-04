class Solution:
    CAPACITY_PENALTY = 0
    def __init__(self, routes, capacities, unassigned, exceeded_capacity, dist, locations, demands, C, penalty=None, obj=None):
        self.routes = routes
        self.capacities = capacities
        self.unassigned = unassigned
        self.exceeded_capacity = exceeded_capacity

        self.dist = dist
        self.locations = locations
        self.demands = demands
        self.max_capacity = C

        self.penalty = max(dist[0][loc] for loc in range(1, len(demands))) * self.CAPACITY_PENALTY if penalty is None else penalty
        self.obj = self.objective(recompute=True) if obj is None else obj

    def route_objective(self, route):
        if len(route) == 0:
            return 0
        return (
            sum(self.dist[loc1][loc2] for loc1, loc2 in zip(route, route[1:]))
            + self.dist[0][route[0]]
            + self.dist[route[-1]][0]
        )
    
    def routes_objective(self):
        return sum(self.route_objective(route) for route in self)

    def exceeded_capacity_penalty(self):
        return sum(
            self.penalty * ((self.capacities[car] - 1) // self.max_capacity)
            for car in self.exceeded_capacity
        )

    def objective(self, recompute=False):
        if recompute:
            self.obj = self.routes_objective() + self.exceeded_capacity_penalty()
        return self.obj

    def incremental_remove(self, car, idx):
        loc2 = self.routes[car][idx]
        loc1 = self.routes[car][idx - 1] if 0 <= idx - 1 else 0
        loc3 = self.routes[car][idx + 1] if idx + 1 < len(self.routes[car]) else 0
        res = self.obj + self.dist[loc1][loc3] - self.dist[loc1][loc2] - self.dist[loc2][loc3]
        exceeded_curr = 0 if self.capacities[car] == 0 else (self.capacities[car] - 1) // self.max_capacity
        exceeded_after = 0 if self.capacities[car] - self.demands[loc2] == 0 else (self.capacities[car] - self.demands[loc2] - 1) // self.max_capacity
        res -= self.penalty * (exceeded_curr - exceeded_after)
        return res

    def remove(self, car, idx):
        loc = self.routes[car][idx]
        self.obj = self.incremental_remove(car, idx)
        self.unassigned.add(loc)
        self.routes[car].pop(idx)
        self.capacities[car] -= self.demands[loc]
        if self.capacities[car] <= self.max_capacity and car in self.exceeded_capacity:
            self.exceeded_capacity.remove(car)

    def incremental_add(self, car, idx, loc2):
        if len(self.routes[car]) == 0:
            loc1, loc3 = 0, 0
        elif idx == 0:
            loc1 = 0
            loc3 = self.routes[car][0]
        elif idx == len(self.routes[car]):
            loc1 = self.routes[car][-1]
            loc3 = 0
        else:
            loc1 = self.routes[car][idx - 1]
            loc3 = self.routes[car][idx]
        res = self.obj - self.dist[loc1][loc3] + self.dist[loc1][loc2] + self.dist[loc2][loc3]
        exceeded_curr = 0 if self.capacities[car] == 0 else (self.capacities[car] - 1) // self.max_capacity
        exceeded_after = 0 if self.capacities[car] + self.demands[loc2] == 0 else (self.capacities[car] + self.demands[loc2] - 1) // self.max_capacity
        res += self.penalty * (exceeded_after - exceeded_curr)
        return res

    def add(self, car, idx, loc):
        self.obj = self.incremental_add(car, idx, loc)
        self.routes[car].insert(idx, loc)
        self.unassigned.remove(loc)
        self.capacities[car] += self.demands[loc]
        if not (self.capacities[car] <= self.max_capacity) and car not in self.exceeded_capacity:
            self.exceeded_capacity.add(car)

    def is_feasible(self):
        return not self.unassigned and not self.exceeded_capacity

    def __iter__(self):
        return iter(self.routes)

    def copy(self):
        return Solution(
            [route.copy() for route in self.routes],
            self.capacities.copy(),
            self.unassigned.copy(),
            self.exceeded_capacity.copy(),
            self.dist,
            self.locations,
            self.demands,
            self.max_capacity,
            self.obj,
        )

    def __lt__(self, other):
        return self.objective() < other.objective() and not self == other
    
    def __eq__(self, other):
        return abs(self.objective() - other.objective()) < 1e-5
    
    def __le__(self, other):
        return self < other or self == other

    def __repr__(self):
        if self.is_feasible():
            return f"{self.objective()}"
        return f"{self.objective()}, not feasible: exceeded {len(self.exceeded_capacity)}, unassigned {len(self.unassigned)}"
