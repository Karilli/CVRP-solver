import json
import sys

from CVRPSolver.CVRP.CVRP import solve


def parse(elem):
    elem = "".join(c for c in elem if c.isspace() and c != "'" and c != '"')
    if elem.lower() == "true":
        return True
    if elem.lower() == "false":
        return False
    if elem.isnumeric():
        return int(elem)
    try:
        return float(elem)
    except:
        return elem


def main(instance_path, output_path, conf={}):
    if isinstance(conf, str):
        conf = [items.split(":") for items in conf[1:-1].split(",")]
        conf = {k: parse(v) for k, v in conf}

    with open(instance_path) as f:
        instance = json.load(f)

    N = instance["NumberOfVehicles"]
    C = instance["VehicleCapacity"]

    dist = instance["DistanceMatrix"]
    locations = instance["Coordinates"]
    demands = instance["LocationDemands"]

    sol = solve(dist, locations, demands, N, C, conf)
    res = [[0] + route + [0] for route in sol]

    with open(output_path, "w") as f:
        json.dump(res, f)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(*sys.argv[1:3])
    elif len(sys.argv) == 4:
        main(*sys.argv[1:4])
    else:
        assert 0
