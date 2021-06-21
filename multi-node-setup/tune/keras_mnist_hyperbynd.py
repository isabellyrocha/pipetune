from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import argparse
import sys
import pickle
import numpy as np
import math
import time
import os
import h5py
import keras
import itertools
import ray

from keras.models import Sequential, Input, Model, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv1D, MaxPooling1D
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU
from keras.utils import to_categorical
from keras.datasets import fashion_mnist
from keras.datasets import mnist
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize

from keras.utils import np_utils
from keras import models, layers, optimizers

from ray.tune.integration.keras import TuneReporterCallback
from ray.tune.examples.utils import get_mnist_data
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray import tune

parser = argparse.ArgumentParser()
parser.add_argument(
    "--smoke-test", action="store_true", help="Finish quickly for testing")
parser.add_argument(
    "--ray-address", type=str, help="The Redis address of the cluster.")
args, _ = parser.parse_known_args()


class TrainCNN(tune.Trainable):

    def _read_data(self):
        # Load dataset as train and test sets
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        # Set numeric type to float32 from uint8
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')

        # Normalize value to [0, 1]
        x_train /= 255
        x_test /= 255

        # Transform lables to one-hot encoding
        y_train = np_utils.to_categorical(y_train, 10)
        y_test = np_utils.to_categorical(y_test, 10)

        # Reshape the dataset into 4D array
        x_train = x_train.reshape(x_train.shape[0], 28,28,1)
        x_test = x_test.reshape(x_test.shape[0], 28,28,1)

        return (x_train, y_train), (x_test, y_test)

    def _build_model(self, config):
        #Instantiate an empty model
        model = Sequential()

        # C1 Convolutional Layer
        model.add(layers.Conv2D(6, kernel_size=(5, 5), strides=(1, 1), activation='tanh', input_shape=(28,28,1), padding="same"))

        # S2 Pooling Layer
        model.add(layers.AveragePooling2D(pool_size=(2, 2), strides=(1, 1), padding='valid'))

        # C3 Convolutional Layer
        model.add(layers.Conv2D(16, kernel_size=(5, 5), strides=(1, 1), activation='tanh', padding='valid'))

        # S4 Pooling Layer
        model.add(layers.AveragePooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

        # C5 Fully Connected Convolutional Layer
        model.add(layers.Conv2D(120, kernel_size=(5, 5), strides=(1, 1), activation='tanh', padding='valid'))

        #Flatten the CNN output so that we can connect it with fully connected layers
        model.add(layers.Flatten())

        # FC6 Fully Connected Layer
        model.add(layers.Dense(84, activation='tanh'))

        #Output Layer with softmax activation
        model.add(layers.Dense(10, activation='softmax'))

        sgd = optimizers.SGD(lr=0.01, decay=2*1e-4, momentum=0.9, nesterov=True)

        # Compile the model
        model.compile(
            loss=keras.losses.categorical_crossentropy, 
            optimizer=sgd, 
            metrics=["accuracy"]
        )

        return model

    def _setup(self, config):
        allow_growth() # Must allow memory growth for each tensorflow session created.
        self.config = config
        self.train_data, self.test_data = self._read_data()
        (self.x_train, self.y_train), (self.x_test, self.y_test) = self._read_data()
        self.model = self._build_model(config)
        self.iter = 0
        self.max_iter = math.ceil(len(self.train_data[0])/self.config['batch'])*self.config['epoch']
        self.iter_per_epoch = math.ceil(len(self.train_data[0])/self.config['batch'])
        self.train_gen = batch_generator(*self.train_data, self.config['batch'])
        self.test_gen = batch_generator(*self.test_data, self.config['batch'])

    def _train(self):
        #train_X, train_Y = self.train_data
        #test_X, test_Y = self.test_data
        #self.model.fit(
        #    train_X,
        #    train_Y,
        #    batch_size=self.config['batch'],
        #    epochs=self.config['epoch'],
        #    verbose=1,
        #    validation_data=(test_X, test_Y)
        #)
        #train = next(self.train_gen)
        #self.model.train_on_batch(
        #    *train,
        #    reset_metrics=True
        #) 
        #self.model.fit_generator(
        #    self.train_gen,
        #    steps_per_epoch=self.iter_per_epoch,
        #    epochs=1,
        #    verbose=1,
        #    validation_data=self.test_gen,
        #    validation_steps=math.ceil(len(self.test_data[0])/self.config['batch'])
        #)

        self.model.fit(
            x=self.x_train,
            y=self.y_train, 
            epochs=self.config['epoch'], 
            batch_size=1024, 
            validation_data=self.test_data,#(x_test, y_test), 
            verbose=1
        )

        #loss, error = self.model.test_on_batch(*train, reset_metrics=True)
        #loss, error = self.model.evaluate_generator(
        #    self.test_gen,
        #    steps=math.ceil(len(self.test_data[0])/self.config['batch']),
        #    verbose=1,
        #    max_queue_size=10
        #)
        test_score = self.model.evaluate(self.x_test, self.y_test)

        res_obj = {
#            "mean_absolute_percentage_error": error,
#            "loss": loss,
            "accuracy": test_score,
            "iter": self.iter,
            "max_iter": self.max_iter,
            "iter_per_epoch": self.iter_per_epoch
        }
        self.iter += self.iter_per_epoch
        print(str(self.iter)+'/'+str(self.max_iter))
        return res_obj

    def _save(self, checkpoint_dir):
        file_path = checkpoint_dir + "/model"
        self.model.save(file_path)
        return file_path

    def _restore(self, path):
        # See https://stackoverflow.com/a/42763323
        del self.model
        self.model = load_model(path)

def batch_generator(X, Y, batch_size):
    indices = np.arange(len(X))
    batch=[]
    while True:
        # it might be a good idea to shuffle your data before each epoch
        np.random.shuffle(indices)
        for i in indices:
            batch.append(i)
            if len(batch)==batch_size:
                yield X[batch], Y[batch]
                batch=[]

def allow_growth():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
        # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
            print(e)


def stop(trial_id, res):
#    if res['mean_absolute_percentage_error']<= 5:
#        return True
#    elif (res['iter'] >= 800) and (res['mean_absolute_percentage_error'] > 40):
#        return True
    if res['accuracy'] > 0.9:
        return True
    elif res['iter'] >= 2:
       return True
    if args.smoke_test and res['iter'] >= 5:
        return True
    elif res['iter'] >= res['max_iter']:
        return True
    else:
        return False

if __name__ == "__main__":

    ray.init(address=args.ray_address, redis_password="password")
    sched = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        metric="mean_absolute_percentage_error",
        mode="min",
        max_t=4,
        grace_period=2)

    analysis = tune.run(
        TrainCNN,
        checkpoint_freq=10,
        checkpoint_at_end=True,
        max_failures=5,
        name="exp",
        scheduler=sched,
        stop=stop,
        num_samples=4,
        reuse_actors=False,
        resume=False,
        resources_per_trial={
            "cpu": 2
            #"gpu": 0.5
        },
        config={
            "threads": 2,
#            "lr": tune.sample_from(lambda spec: np.random.uniform(0.001, 0.1)),
#            "filters": tune.sample_from(
#                lambda spec: np.random.randint(32, 512)),
#            "hidden": tune.sample_from(
#                lambda spec: np.random.randint(32, 1024)),
#            "drop": tune.sample_from(
#                lambda spec: np.random.uniform(0.0, 0.5)),
            "batch": tune.sample_from(
                lambda spec: np.random.randint(32, 512)),
            "epoch": tune.sample_from(
                lambda spec: np.random.randint(1, 10))
#            "num_filters": tune.sample_from(
#                lambda spec: np.random.randint(1, 10)),
#            "num_dense": tune.sample_from(
#                lambda spec: np.random.randint(1, 10))
        })

    trials = analysis.trials
    for trial in trials:
        print (trial.metric_analysis['mean_absolute_percentage_error'])
    best_trial = analysis.get_best_trial('mean_absolute_percentage_error', mode='min', scope='all')
    print(best_trial)
    print(best_trial.metric_analysis['mean_absolute_percentage_error'])
    print(best_trial.config)
