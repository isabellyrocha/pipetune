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

class MNIST(Trainable):
    """Example agent whose learning curve is a random sigmoid.
    The dummy hyperparameters "width" and "height" determine the slope and
    maximum reward value reached.
    """
    def _setup(self, config):
        self.timestep = 0
        self.bigdl = BigDL()# = self.config['bigdl']#igDL()
        self.config = config
        self.info = {"timestep": 0}

    def _train(self):
        batch = str(self.config['batch'])
        lr = str(self.config['lr'])
        n_epochs = "1"#str(self.config['epochs'])
        cores = "1"#str(self.config['cores'])
        lrd = str(self.config['lrd'])
        mem = "4"#str(self.config['memory'])
#        if batch == "32":
#            cores = "2"
        ts = self.info['timestep']
        result = self.bigdl.run_mnist(total_executor_cores = cores,
                                      memory = mem,
                                      batch_size = batch,
                                      learning_rate = lr,
                                      learning_rate_decay = lrd,
                                      epochs = n_epochs)
        self.info = result
        self.info['timestep'] = ts+1
#        self.info['duration'] = int(self.info['duration'])/(ts+1)
        #self.info['timestep'] = ts+1
        return result

    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps(self.info))
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.info = json.loads(f.read())


class MNIST_V2(Trainable):
    """Example agent whose learning curve is a random sigmoid.
    The dummy hyperparameters "width" and "height" determine the slope and
    maximum reward value reached.
    """
    def _setup(self, config):
        self.timestep = 0
        self.bigdl = BigDL()# = self.config['bigdl']#igDL()
        self.config = config
        #if not self.info:
        self.info = {"timestep": 0}

    def _train(self):
        batch = str(self.config['batch'])
        lr = str(self.config['lr'])
        n_epochs = "1"#str(self.config['epochs'])
        print(self.info)
#        cores = "2"
        if not metrics.exists_duration("mnist",batch,"1","8"):
            cores = "1"
        elif not metrics.exists_duration("mnist",batch,"16","8"):
            cores = "16"
#        elif metrics.exists_duration("mnist",batch,"1","4") and metrics.exists_duration("mnist",batch,"16","4"):
        else:
            duration_1 = metrics.query_duration("mnist",batch,"1","8")
            duration_16 = metrics.query_duration("mnist",batch,"16","8")
            if duration_1 < duration_16:
                cores = "1"
            else: 
                cores = "16"
       # cores = str(self.config['cores'])
        lrd = str(self.config['lrd'])
        mem = "8"#str(self.config['memory'])
#        if batch == "32":
#            cores = "2"
        ts = self.info['timestep']
        result = self.bigdl.run_mnist(total_executor_cores = cores,
                                      memory = mem,
                                      batch_size = batch,
                                      learning_rate = lr,
                                      learning_rate_decay = lrd,
                                      epochs = n_epochs,
                                      info_in = self.info)
        self.info = result
        print(self.info)
        self.info['timestep'] = ts+1
        client = InfluxDBClient('localhost', 8086, 'root', 'root', 'pipetune')
        if not metrics.exists_duration("mnist",batch,cores,mem):
#            try:
            metrics.write_metrics_influxdb("mnist", batch, cores, mem, utils.timestamp(),self.info['duration'], self.info['accuracy'], float(self.info['energy']), client)
#            except:
#                print("An exception occured")
#        self.info['duration'] = int(self.info['duration'])/(ts+1)
        #self.info['timestep'] = ts+1
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
        checkpoint_at_end=True,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop={"training_iteration": 10},
        num_samples=1,
        reuse_actors=True,
        resume=False,
        resources_per_trial={
            "cpu": 2
            #"gpu": 0.5
        },
        config={
#            "epochs": tune.sample_from(
#                lambda spec: np.random.randint(10, 20)),
            #    lambda spec: np.random.randint(1, 100)),
            "lr": tune.sample_from(
                lambda spec: np.random.uniform(0.001, 0.1)),
            #    lambda spec: np.random.uniform(0.001, 0.1)),
            "batch": tune.sample_from([32, 64, 128, 256, 512, 1024]),#tune.grid_search([64,256,1024]),
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
        MNIST_V2,
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
            "cpu": 2
            #"gpu": 0.5
        },
        config={
#            "epochs": tune.sample_from(
#                lambda spec: np.random.randint(10, 20)),
            #    lambda spec: np.random.randint(1, 100)),
            "lr": tune.sample_from(
                lambda spec: np.random.uniform(0.001, 0.1)),
            #    lambda spec: np.random.uniform(0.001, 0.1)),
            "batch": tune.sample_from([32, 64, 128, 256, 512, 1024]),#tune.grid_search([64,256,1024]),
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
