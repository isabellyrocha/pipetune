import argparse
import json
import os
import random
import numpy as np
import ray
from ray import tune
from ray.tune import Trainable, run, Experiment, sample_from
from ray.tune.schedulers import AsyncHyperBandScheduler
from bigdl.bigdl import BigDL

class MNIST(Trainable):
    """Example agent whose learning curve is a random sigmoid.
    The dummy hyperparameters "width" and "height" determine the slope and
    maximum reward value reached.
    """
    def _setup(self, config):
        self.timestep = 0
        self.bigdl = BigDL()

    def _train(self):
        self.timestep += 1
        batch = str(self.config['batch'])
        print(batch)
        result = self.bigdl.run_mnist(batch_size = batch)
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

def runParameter():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    # Hyperband early stopping, configured with `episode_reward_mean` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    hyperband = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        metric="duration",
        mode="min",
        max_t=1)

    exp = Experiment(
        name="hyperband_test",
        run=MNIST,
        num_samples=1,
        stop={"training_iteration": 1 if args.smoke_test else 99999},
        config={
            "batch": tune.grid_search([32,64,512,1024])#tune.sample_from(lambda spec: np.random.randint(64, 1024))
            #"cores": tune.grid_search([1,2,4])
        })

    analysis = run(exp, scheduler=hyperband, resume=False) # resources_per_trial={"cpu": 2, "gpu": 1}
    print("Best config is", analysis.get_best_config(metric="duration"))

