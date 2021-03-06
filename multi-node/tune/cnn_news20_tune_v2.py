import argparse
import json
import os
import random
import numpy as np
import ray
from ray import tune
from ray.tune import Trainable, run, Experiment, sample_from
from ray.tune.schedulers import AsyncHyperBandScheduler, HyperBandScheduler
from bigdl.BigDL import BigDL
from utils import utils, metrics
from influxdb import InfluxDBClient

class text_classifier(Trainable):
    def _setup(self, config):
        self.timestep = 0
        self.bigdl = BigDL()# = self.config['bigdl']#igDL()
        self.config = config
        self.info = {'timestep': 0}

    def _train(self):
        batch = str(self.config['batch'])
        lr = str(self.config['lr'])
        ed = str(self.config['embedding_dim'])
        mem = str(self.config['memory'])
        cores = str(self.config['cores'])
        mod = "lstm"
        m_epochs = "3"

        result = self.bigdl.run_textclassifier(model = mod,
                                      total_executor_cores = cores,
                                      memory = mem,
                                      batchSize = batch,
                                      embedding_dim = ed,
                                      learning_rate = lr,
                                      max_epochs = m_epochs)
        self.info = result
        return result

    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps(self.info))
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.info = json.loads(f.read())

def runParameter():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
#    ray.init()

    # Hyperband early stopping, configured with `episode_reward_mean` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    sched = HyperBandScheduler(
        time_attr="training_iteration",
        metric="duration",
        mode="min",
        max_t=20)

    analysis = tune.run(
        text_classifier,
        checkpoint_freq=1,
        checkpoint_at_end=False,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop={"training_iteration": 1},
        num_samples=5,
        reuse_actors=False,
        resume=False,
        resources_per_trial={
            "cpu": 8
        },
        config={
            "lr": tune.sample_from(
                lambda spec: np.random.uniform(0.005, 0.5)),
            "batch": tune.sample_from(
                lambda spec: random.sample([32, 64, 512, 1024],1)[0]),
            "embedding_dim": tune.sample_from(
                lambda spec: random.sample([100, 200, 300],1)[0]),
            "cores": tune.sample_from(
                lambda spec: random.sample([4, 8, 16],1)[0]),
            "memory": tune.sample_from(
                lambda spec: random.sample([8, 16, 32],1)[0])
        })

    trials = analysis.trials
    for trial in trials:
        print (trial.metric_analysis['ratio'])
    best_trial = analysis.get_best_trial('ratio', mode='max', scope='all')
    print(best_trial)
    print(best_trial.metric_analysis['ratio'])
    print(best_trial.config)
