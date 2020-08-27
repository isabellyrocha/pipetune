from pathlib import Path
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
from utils.Profiler import Profiler
from utils.GroundTruth import GroundTruth
from influxdb import InfluxDBClient

class TRAIN(Trainable):
    def _setup(self, config):
        self.config = config
        self.bigdl = BigDL()
        self.profiler = Profiler()
        self.ground_truth = GroundTruth()

    def _setSysParameters(self, config, cores, memory):
        config['total_executor_cores'] = str(cores)
        config['executor_cores'] = str(int(int(cores)/4))
        config['executor_memory'] = "%sG" % memory

    def _getBestConfig(self, probing):
        result = ("16", "8")
        min_duration = 0
        for key in probing.keys():
            duration = probing[key]
            if duration < min_duration:
                min_duration = duration
                result = key
        return result

    def _train(self):
        config_file = "%s/pipetune/bigdl/config/test.json" % Path.home()
        config = utils.read_json(config_file)

        config['batch_size'] = str(self.config['batch'])
        config['learning_rate'] = str(self.config['lr'])
        config['learning_rate_decay'] = str(self.config['lrd'])

        cores = "16"
        memory = "8"
        n_epochs = 5

        self._setSysParameters(config, cores, memory)

        #### probing phase ###
        print("STARTING FIRST EPOCH..")
#        result = self.bigdl.run_lenet5(config, cores, memory, batch, lr, lrd, "1", True)
        result = self.bigdl.run(config, True)
        print("STARTING FIRST EPOCH..")
        gt_result = ("16", "4")#self.ground_truth.getConfig(metrics, config['batch_size'])
        if gt_result:
            (cores, memory) = gt_result    
            self._setSysParameters(config, cores, memory)
#            remaining_result = self.bigdl.run_lenet5(config, cores, memory, batch, lr, lrd, str(n_epochs-1))
            config['endTriggerNum'] = str(n_epochs-1)
            remaining_result = self.bigdl.run(config)
            result['duration'] = result['duration'] + remaining_result['duration']
        else:
            probing = {}
            probing[(cores, memory)] = result['duration']
            for trial_cores in ["4", "8"]:
                self._setSysParameters(config, trial_cores, memory)
                trial_result = self.bigdl.run(config, True)
#                trial_result  = self.bigdl.run_lenet5(config, trial_cores, memory, batch, lr, lrd, "1", True)
                probing[(trial_cores, memory)] = trial_result['duration']
                result['duration'] = result['duration'] + trial_result['duration']
            for trial_memory in ["4"]:
                self._setSysParameters(config, cores, trial_memory)
                trial_result = self.bigdl.run(config, True)
                probing[(cores, trial_memory)] = trial_result['duration']
#                trial_result = self.bigdl.run_lenet5(config, cores, trial_memory, batch, lr, lrd, "1", True)
                result['duration'] = result['duration'] + trial_result['duration']
            config['endTriggerNum'] = str(n_epochs-4)
            (cores, memory) = self._getBestConfig(probing)
            self._setSysParameters(config, cores, memory)
            remaining_result = self.bigdl.run(config)
#            remaining_result = self.bigdl.run_lenet5(config, cores, memory, batch, lr, lrd, str(n_epochs-4))
            result['duration'] = result['duration'] + remaining_result['duration']        
        return result        

    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.info = json.loads(f.read())

def stop(trial_id, res):
    if float(res['accuracy']) >= 0.9:
        return True
    elif res['iter'] >= 10:
        return True
    else:        
        return False

def runParameter():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    sched = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        metric="accuracy",
        mode="max",
        max_t=20)

    analysis = tune.run(
        TRAIN,
        checkpoint_freq=1,
        checkpoint_at_end=False,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop={"training_iteration": 1},
        num_samples=1,
        reuse_actors=False,
        resume=False,
        resources_per_trial={
            "cpu": 8,
            "gpu": 0
        },
        config={
#            "epochs": tune.sample_from(
#                lambda spec: np.random.randint(1, 100)),
            "batch": tune.sample_from([1024, 512, 32, 64]),
            "lr": tune.sample_from(
                lambda spec: np.random.uniform(0.001, 0.1)),
            "lrd": tune.sample_from(
                lambda spec: np.random.uniform(0.2, 0.0002))
            #"cores": tune.sample_from([1, 16]),
            #"executor_cores": tune.sample_from([1, 2, 4]),#tune.grid_search([1,2,4])
            #"memory": tune.sample_from([2, 4])
        })
    trials = analysis.trials
    for trial in trials:
        print (trial.metric_analysis['accuracy'])
    best_trial = analysis.get_best_trial('accuracy', mode='max', scope='all')
    print(best_trial)
    print(best_trial.metric_analysis['accuracy'])
    print(best_trial.config)
