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
        m_epochs = "1"#str(self.config['epochs'])
        cores = "16"#str(self.config['cores'])
        ed = str(self.config['embedding_dim'])
        mem = "32"#str(self.config['memory'])
        ts = self.info['timestep']
        result = self.bigdl.run_textclassifier(total_executor_cores = cores,
                                      memory = mem,
                                      batchSize = batch,
                                      embedding_dim = ed,
                                      learning_rate = lr,
                                      max_epochs = m_epochs)
        self.info = result
        self.info['timestep'] = ts+1
        return result

    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps(self.info))
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.info = json.loads(f.read())

def runPipetune():
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
        max_t=20)

    analysis = tune.run(
        text_classifier,
        checkpoint_freq=1,
        checkpoint_at_end=True,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop={"training_iteration": 10},
        num_samples=1,
        reuse_actors=True,
        resume=False,
        resources_per_trial={
            "cpu": 8
            #"gpu": 0.5
        },
        config={
#            "epochs": tune.sample_from(
#                lambda spec: np.random.randint(10, 20)),
            #    lambda spec: np.random.randint(1, 100)),
            "lr": tune.sample_from(
                lambda spec: np.random.uniform(0.005, 0.5)),
            #    lambda spec: np.random.uniform(0.001, 0.1)),
            "batch": tune.sample_from([32, 64, 128, 256, 512, 1024]),#tune.grid_search([64,256,1024]),
            "embedding_dim": tune.sample_from([100, 200, 300])
            #"cores": tune.sample_from([1, 16]),
            #"executor_cores": tune.sample_from([1, 2, 4]),#tune.grid_search([1,2,4])
            #"memory": tune.sample_from([2, 4])
        })

    trials = analysis.trials
    for trial in trials:
        print (trial.metric_analysis['duration'])
    best_trial = analysis.get_best_trial('duration', mode='min', scope='all')
    print(best_trial)
    print(best_trial.metric_analysis['duration'])
    print(best_trial.config)
