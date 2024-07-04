import traceback
from subprocess import Popen
from sys import stderr, stdout
from CVRPSolver import CONFIG_SPACE
from CVRPSolver.validation import validate
from amltk.optimization.optimizers.smac import SMACOptimizer
from amltk.optimization import Metric, History
from amltk.pipeline import Searchable
from amltk.store import PathBucket
from amltk.scheduling import Scheduler
from time import perf_counter


SOLVER = "./main.py"
DATA = "./data"
TEMP = "./SMAC-large"

INSTANCES = [195, 336, 670, 979]  # [32, 45, 55, 66, 78, 80]
SEED = 42
OPT_NAME = "CVRP"
TIME = 12*60*60
BUDGET=(1, 5*60)
N_WORKERS = 2


def shell(command, out=stdout, err=stderr, silent=True):
    if not silent:
        print(">>>", command)
    code = Popen(command, shell=True, stdout=out, stderr=err).wait()
    if code != 0:
        raise ValueError(f"{command} failed with code {code}.")


def target_function(trial):
    config = dict(trial.config)
    budget = trial.fidelities["budget"]
    config_id = int(trial.name.split("_")[1].split("=")[1])

    config["SEED"] = SEED
    config["TIME_LIMIT"] = budget
    trial.store({"config.json": trial.config})
    config = str(config).replace(" ", "").replace("'", "").replace(f"{OPT_NAME}:", "")

    res = []
    times = []
    for instance in INSTANCES:
        instance_path = f"{DATA}/cvrp_{instance}.json"
        out_path = f"{trial.bucket.path}/cvrp_{instance}.json"
        trial.bucket[f"cvrp_{instance}.json"] = {}

        try:
            t = perf_counter()
            shell(f"pypy3 {SOLVER} {instance_path} {out_path} '{config}'")
            t = perf_counter() - t
            my_score, global_min = validate(instance_path, out_path)
        except Exception as e:
            tb = traceback.format_exc()
            trial.store({"exception.txt": f"{e}\n {tb}"})
            return trial.fail(e, tb)

        res.append(100 * (my_score / global_min - 1))
        times.append(t)
        trial.store({
            f"cvrp_{instance}.json": {
                "budget": budget,
                "elapsed_time": times[-1],
                "score": res[-1]
            },
        })

    score = sum((x**3) / (abs(x)+1e-18) for x in res)**(1/2)
    report = trial.success(score=score)

    trial.summary["score"] = score
    trial.summary["res"] = res
    trial.summary["times"] = times
    trial.summary["budget"] = budget
    trial.summary["config_id"] = config_id
    
    trial.store({
        "result.json": {
            "budget": budget, 
            "elapsed_time": sum(times), 
            "times": times, 
            "res": res, 
            "score": score
        },
        "report.pkl": report
    })

    print(f"Config-id: {config_id}, budget: {budget:.2f}, score: {score:.2f} - {[round(n, 2) for n in res]}")
    return report


def optimize(timeout, fnc, space, metric, bucket, budget, opt_name, n_workers, seed):
    def launch_initial_tasks() -> None:
        trial = optimizer.ask()
        task.submit(trial)

    def process_result_and_launch(_, report) -> None:
        history.add(report)
        if scheduler.running():
            optimizer.tell(report)
            trial = optimizer.ask()
            task.submit(trial)

    space = Searchable(space=space, name=opt_name)
    scheduler = Scheduler.with_processes(n_workers)
    task = scheduler.task(fnc)
    optimizer = SMACOptimizer.create(
        space=space, 
        fidelities={"budget": budget}, 
        metrics=metric, 
        bucket=bucket, 
        seed=seed,
        continue_from_last_run=True
    )

    history = History()
    res = []
    for name in bucket:
        report = (bucket / name)["report.pkl"].get()
        if report is not None:
            history.add(report)
            res.append((
                report.trial.summary['config_id'],
                report.trial.summary['budget'],
                report.trial.summary['score'],
                report.trial.summary['res']
            ))

    for config_id, budget, score, res in sorted(res, key=lambda i: -i[2]):
        print(f"Config-id: {config_id}, budget: {budget:.2f}, score: {score:.2f} - {[round(n, 2) for n in res]}")

    scheduler.on_start(launch_initial_tasks, repeat=n_workers)
    task.on_result(process_result_and_launch)
    scheduler.run(timeout=timeout, wait=False)
    return history


def main():
    history = optimize(
        timeout=TIME,
        fnc=target_function,
        space=CONFIG_SPACE,
        metric=Metric(name="score", minimize=True),
        bucket=PathBucket(TEMP),
        budget=BUDGET,
        opt_name=OPT_NAME,
        n_workers=N_WORKERS,
        seed=SEED
    )
    bucket = PathBucket(".")
    df = history.df(profiles=True, configs=True, summary=False, metrics=True)
    bucket[f"{TEMP}.csv"] = df

    print(f"Number of configurations: {len(history)}")
    try:
        best_trial = history.filter(lambda report: abs(report.trial.fidelities["budget"] - BUDGET[1]) < 0.0001).best()
        print("Best config:")
        for k, v in best_trial.config.items():
            print(f"\t{k}: {v}")
    except:
        print("No configuration with max budget was evaluated.")


if __name__ == "__main__":
    main()
