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
from utils.Profiler import Profiler
from utils.GroundTruth import GroundTruth
from influxdb import InfluxDBClient

class MNIST(Trainable):
    def _setup(self, config):
        self.timestep = 0
        self.bigdl = BigDL()
        self.config = config
        self.profiler = Profiler()
        self.ground_truth = GroundTruth()
        self.info = {}

    def _train(self):
        batch = str(self.config['batch'])
        lr = str(self.config['lr'])
        lrd = str(self.config['lrd'])

        cores = "16"
        memory = "8"
        n_epochs = 5


        #### probing phase ###
#        self.profiler.startMeasuring("mnist_test")
        result = self.bigdl.run_mnist_off(total_executor_cores = cores,
                                      memory = memory,
                                      batch_size = batch,
                                      learning_rate = lr,
                                      learning_rate_decay = lrd,
                                      epochs = "1")
#        self.profiler.stopMeasuring()
        metrics = self.profiler.getMetrics("mnist_%s_%s_%s" % (batch, lr, lrd))
        (cores, memory) = self.ground_truth.getConfig(metrics)
        ######################

        result = self.bigdl.run_mnist(total_executor_cores = cores,
                                      memory = memory,
                                      batch_size = batch,
                                      learning_rate = lr,
                                      learning_rate_decay = lrd,
                                      epochs = str(n_epochs-1))
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

#if __name__ == "__main__":

def stop(trial_id, res):
    if float(res['accuracy']) >= 0.99:
        return True
#    elif (res['iter'] >= 800) and (res['mean_absolute_percentage_error'] > 40):
#        return True
#    elif args.smoke_test and res['iter'] >= 5:
#        return True
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

    # Hyperband early stopping, configured with `episode_reward_mean` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    sched = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        metric="duration",
        mode="min",
        max_t=20)

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

    analysis = tune.run(
        MNIST,
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
            "cpu": 8
            #"gpu": 0.5
        },
        config={
#            "epochs": tune.sample_from(
#                lambda spec: np.random.randint(10, 20)),
            #    lambda spec: np.random.randint(1, 100)),
            "lr": tune.sample_from(
                lambda spec: np.random.uniform(0.001, 0.1)),
            #    lambda spec: np.random.uniform(0.001, 0.1)),
            "batch": tune.sample_from([1024, 512, 32, 64]),#tune.grid_search([64,256,1024]),
            "lrd": tune.sample_from(
                lambda spec: np.random.uniform(0.2, 0.0002)),
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


def runPipetune():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    # Hyperband early stopping, configured with `episode_reward_mean` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    sched = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        metric="duration",
        mode="min",
        max_t=20)

    analysis = tune.run(
        MNIST,
        checkpoint_freq=1,
        checkpoint_at_end=False,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop={"training_iteration": 10},
        num_samples=1,
        reuse_actors=False,
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
                lambda spec: np.random.uniform(0.001, 0.1)),
            #    lambda spec: np.random.uniform(0.001, 0.1)),
            "batch": tune.sample_from([1024, 32, 64, 128, 256, 512, 1024]),#tune.grid_search([64,256,1024]),
            "lrd": tune.sample_from(
                lambda spec: np.random.uniform(0.2, 0.0002)),
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
