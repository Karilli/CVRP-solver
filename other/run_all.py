##############################################
import sys, os                              ##
sys.path.insert(0, os.path.abspath("."))    ##
##############################################

from main import main
from CVRPSolver.validation import validate


OUT = "./out.json"
INSTANCES = [32, 45, 55, 66, 78, 80, 195, 336, 670, 979]
conf = {"TIME_LIMIT": 3*60}


print(f"Time limit: {conf['TIME_LIMIT']} s.")
for instance in INSTANCES:
    instance = f"./data/cvrp_{instance}.json"
    main(instance, OUT, conf)
    my_score, global_min = validate(instance, OUT)
    print(f"Instance {instance} score: {100 * (my_score / global_min - 1):.2f} %, {my_score}/{global_min}")
