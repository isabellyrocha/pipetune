#from __future__ import print_function
from tensorflow import keras
from keras.datasets import cifar10
#from keras.preprocessing.image import ImageDataGenerator
#from keras.models import Sequential
#from keras.layers import Dense, Dropout, Activation, Flatten
#from keras.layers import Conv2D, MaxPooling2D
import os, sys
from optparse import OptionParser
import keras.backend
from bigdl.examples.keras.keras_utils import *
#from bigdl.util.common import *
#from bigdl.nn.layer import *
#from bigdl.optim.optimizer import *
#from bigdl.nn.criterion import *

# Build model with Keras
def build_keras_model(x_train, num_classes):
    """
    Define model in Keras 1.2.2
    """
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Activation, Flatten
    from keras.layers import Convolution2D, MaxPooling2D, Conv2D

    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same', input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))
    return model


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--appName", dest="appName",default="cifar10")
    parser.add_option("-a", "--action", dest="action", default="train")
    parser.add_option("-b", "--batchSize", type=int, dest="batchSize", default="128")
    parser.add_option("-l", "--learningRate", dest="learningRate", default="0.001")
    parser.add_option("-k", "--learningrateDecay", dest="learningrateDecay", default="1e-6")
    parser.add_option("-t", "--endTriggerType", dest="endTriggerType", default="epoch")
    parser.add_option("-n", "--endTriggerNum", type=int, dest="endTriggerNum", default="20")
    parser.add_option("-j", "--executorCores", dest="executorCores", default="4")
    (options, args) = parser.parse_args(sys.argv)

    (train_images, train_labels), (test_images, test_labels) = cifar10.load_data()
    #train_images = keras.utils.to_categorical(train_labels, 10)
    #test_images = keras.utils.to_categorical(test_labels, 10)

    # The data, split between train and test sets:
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    # Convert class vectors to binary class matrices.
    #y_train = keras.utils.to_categorical(y_train, 10)
    #y_test = keras.utils.to_categorical(y_test, 10)

    print('x_train shape: ', x_train.shape[1:])

    keras_model = build_keras_model(x_train, 10)
    json_path = "/home/ubuntu/pipetune/applications/cifar10.json"
    save_keras_definition(keras_model, json_path)

    from bigdl.util.common import *
    from bigdl.nn.layer import *
    from bigdl.optim.optimizer import *
    from bigdl.nn.criterion import *

    # Load the JSON file to a BigDL model
    bigdl_model = Model.load_keras(json_path=json_path)

    sc = SparkContext(appName=options.appName, conf=create_spark_conf())

    redire_spark_logs()
    show_bigdl_info_logs()
    init_engine()

    learning_rate=float(options.learningRate)
    learning_rate_decay=float(options.learningrateDecay)

    #(train_images, train_labels), (test_images, test_labels) = cifar10.load_data()
    #training_mean = np.mean(train_images)
    #training_std = np.std(train_images)
    #test_mean = np.mean(test_images)
    #test_std = np.std(test_images)

    images = sc.parallelize(train_images)
    labels = sc.parallelize(train_labels+1)
    record = images.zip(labels)
    train_data = record.map(lambda rec_tuple: (normalizer(rec_tuple[0], training_mean, training_std), rec_tuple[1])).map(lambda t: Sample.from_ndarray(t[0], t[1]))

    images = sc.parallelize(test_images)
    labels = sc.parallelize(test_labels+1)
    record = images.zip(labels)
    test_data = record.map(lambda rec_tuple: (normalizer(rec_tuple[0], test_mean, test_std), rec_tuple[1])).map(lambda t: Sample.from_ndarray(t[0], t[1]))

    optimizer = Optimizer(
        model=bigdl_model,
        training_rdd=train_data,
        criterion=ClassNLLCriterion(),
        optim_method=RMSprop(learningrate=learning_rate, learningrate_decay=learning_rate_decay),#, momentum=0.9, dampening=0.0, nesterov=True),
        end_trigger=MaxEpoch(int(options.endTriggerNum)),
        batch_size=options.batchSize)

    validate_optimizer(optimizer, test_data)
    trained_model = optimizer.optimize()
    parameters = trained_model.parameters()
