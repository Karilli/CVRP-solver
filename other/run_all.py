##############################################
import sys, os                              ##
sys.path.insert(0, os.path.abspath("."))    ##
##############################################

from main import main
from CVRPSolver.validation import validate

print("[WARNING]: This script uses eval on arguments passed via terminal. Use this with causion.")
OUT = "./out.json"
CONFIG = {"TIME_LIMIT": eval(sys.argv[1]) if 2 <= len(sys.argv) else 3*60}
INSTANCES = eval(sys.argv[2]) if 3 <= len(sys.argv) else [32, 45, 55, 66, 78, 80, 195, 336, 670, 979]


print(f"Time limit: {CONFIG['TIME_LIMIT']} s.")
for instance in INSTANCES:
    instance = f"./data/cvrp_{instance}.json"
    main(instance, OUT, CONFIG)
    my_score, global_min = validate(instance, OUT)
    print(f"Instance {instance} score: {100 * (my_score / global_min - 1):.2f} %, {my_score}/{global_min}")
