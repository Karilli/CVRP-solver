import json


def validate(instance_path, solution_path):
    with open(instance_path) as f:
        instance = json.load(f)

    with open(solution_path) as f:
        routes = json.load(f)

    distance_matrix = instance["DistanceMatrix"]
    vehicle_capacity = instance["VehicleCapacity"]
    location_demands = instance["LocationDemands"]

    for route in routes:
        route_total_demand = sum([location_demands[loc] for loc in route])
        assert route_total_demand <= vehicle_capacity

    from collections import Counter
    location_counts = Counter(loc for route in routes for loc in route)
    assert len(location_counts) == len(location_demands), f"{len(location_counts)} {len(location_demands)}"

    for loc, count in location_counts.items():
        assert loc == 0 or count == 1

    for route in routes:
        assert route[0] == 0 and route[-1] == 0
        assert 0 not in route[1:-1]

    def total_route_distance(route, distance_matrix):
        total = 0
        for i in range(1, len(route)):
            prev_loc, curr_loc = route[i - 1], route[i]
            total += distance_matrix[prev_loc][curr_loc]
        return total

    total_distance = sum([total_route_distance(route, distance_matrix) for route in routes])
    return total_distance, instance['GlobalBestTotalDistance']
