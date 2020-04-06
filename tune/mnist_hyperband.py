import argparse
import json
import os
import random
import numpy as np
import ray
from ray import tune
from ray.tune import Trainable, run, Experiment, sample_from
from ray.tune.schedulers import AsyncHyperBandScheduler, HyperBandScheduler
from bigdl.bigdl import BigDL

class MNIST(Trainable):
    """Example agent whose learning curve is a random sigmoid.
    The dummy hyperparameters "width" and "height" determine the slope and
    maximum reward value reached.
    """
    def _setup(self, config):
        self.timestep = 0
        self.bigdl = self.config['bigdl']#igDL()
        self.config = config

    def _train(self):
        self.timestep += 1
        batch = str(self.config['batch'])
        cores = str(self.config['cores'])
        result = self.bigdl.run_mnist(batch_size = batch,
                                      total_executor_cores = cores)
        result["iter"] = self.timestep
        return result

    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps({"timestep": self.timestep}))
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.timestep = json.loads(f.read())["timestep"]

#if __name__ == "__main__":

def stop(trial_id, res):
    if float(res['accuracy']) >= 0.99:
        return True
#    elif (res['iter'] >= 800) and (res['mean_absolute_percentage_error'] > 40):
#        return True
#    elif args.smoke_test and res['iter'] >= 5:
#        return True
    elif res['iter'] >= 1:
        return True
    else:        
        return False

def runParameter():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    # Hyperband early stopping, configured with `episode_reward_mean` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    sched = HyperBandScheduler(
        time_attr="training_iteration",
        metric="duration",
        mode="min",
        max_t=1)

#    exp = Experiment(
#        name="hyperband_test",
#        run=MNIST,
#        num_samples=1,
#        stop={"training_iteration": 1 if args.smoke_test else 99999},
#        config={
#            "batch": np.random.randint(32,1024) #tune.grid_search([32,64,512,1024])#tune.sample_from(lambda spec: np.random.randint(64, 1024))
            #"cores": tune.grid_search([1,2,4])
#        })

#    analysis = run(exp, scheduler=hyperband, resume=False, resources_per_trial={"cpu": 2})
#    print("Best config is", analysis.get_best_config(metric="duration"))

    bigdl = BigDL()

    analysis = tune.run(
        MNIST,
        checkpoint_freq=10,
        checkpoint_at_end=True,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop=stop,#stop,
        num_samples=1,
        reuse_actors=False,
        resume=False,
        #resources_per_trial={
        #    "cpu": 1
            #"gpu": 0.5
        #},
        config={
            "bigdl": bigdl,
            "batch": tune.grid_search([64,256,1024]),
            "cores": tune.grid_search([1,2,4])
        })

    trials = analysis.trials
    for trial in trials:
        print (trial.metric_analysis['ratio'])
    best_trial = analysis.get_best_trial('ratio', mode='max', scope='all')
    print(best_trial)
    print(best_trial.metric_analysis['ratio'])
    print(best_trial.config)
