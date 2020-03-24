from bigdl.bigdl import BigDL
import argparse
import json
import os
import random
import numpy as np
import ray
from ray import tune
from ray.tune import Trainable, run, Experiment, sample_from
from ray.tune.schedulers import HyperBandScheduler

class MNIST(Trainable):
    """Example agent whose learning curve is a random sigmoid.
    The dummy hyperparameters "width" and "height" determine the slope and
    maximum reward value reached.
    """
    def _setup(self, config):
        self.timestep = 0

    def _train(self):
        self.timestep += 1
        v = np.tanh(float(self.timestep) / self.config.get("cores", 1))
        result = bigdl.run(str(self.config.get("cores", 1)), "1024")#self.config.get("batch", 1024))
        # Here we use `episode_reward_mean`, but you can also report other
        # objectives such as loss or accuracy.
        return {"episode_reward_mean": result[1]}

    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps({"timestep": self.timestep}))
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.timestep = json.loads(f.read())["timestep"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    # Hyperband early stopping, configured with `episode_reward_mean` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    hyperband = HyperBandScheduler(
        time_attr="training_iteration",
        metric="time_total_s",
        mode="max",
        max_t=100)

    exp = Experiment(
        name="hyperband_test",
        run=MNIST,
        num_samples=1,
        stop={"training_iteration": 1 if args.smoke_test else 99999},
        config={
            "batch": tune.sample_from(lambda spec: np.random.randint(1024, 1024))
            #"cores": tune.grid_search([1,2,4])
        })

    analysis = run(exp, scheduler=hyperband) # resources_per_trial={"cpu": 2, "gpu": 1}
    print("Best config is", analysis.get_best_config(metric="time_total_s"))

