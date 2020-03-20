from __future__ import print_function, division
import numpy
from keras.utils import np_utils
from optparse import OptionParser
#from keras import optimizers

#from keras.datasets import cifar10
#from keras.layers import Input, Dense, Reshape, Flatten, Dropout, concatenate
#from keras.layers import BatchNormalization, Activation, ZeroPadding2D
#from keras.layers.advanced_activations import LeakyReLU
#from keras.regularizers import l2

#from keras.utils import np_utils
#from keras.layers.convolutional import UpSampling2D, Conv2D, MaxPooling2D
#from keras.models import Sequential, Model
#from keras.optimizers import Adam, SGD
#from keras import backend as K
import gzip
from keras.datasets import mnist, cifar100,cifar10
#from keras.utils import np_utils
from optparse import OptionParser
#from bigdl.models.lenet.utils import *
from bigdl.dataset.transformer import *
from bigdl.nn.layer import *
#from bigdl.nn.topology import *
from bigdl.nn.criterion import *
from bigdl.optim.optimizer import *
from bigdl.util.common import *
#from bigdl.nn.keras.layer import Dense

#from bigdl.nn.keras.topology import Sequential
#from bigdl.nn.keras.layer import *
TRAIN_MEAN = 0.13066047740239506 * 255
TRAIN_STD = 0.3081078 * 255
TEST_MEAN = 0.13251460696903547 * 255
TEST_STD = 0.31048024 * 255
#K.tensorflow_backend.set_image_dim_ordering('th')


def validate_optimizer(optimizer, test_data):
    """
    Set validation and checkpoint for distributed optimizer.
    """
    optimizer.set_validation(
        batch_size=1024,
        val_rdd=test_data,
        trigger=EveryEpoch(),
        val_method=[Top1Accuracy()]
    )
    optimizer.set_checkpoint(EveryEpoch(), "/tmp/lenet5")

def build_model_bc(class_num):
    model = Sequential()
    model.add(Reshape([3, 32, 32]))
    model.add(SpatialConvolution(3, 32, 5, 5))
    model.add(ELU())
    model.add(SpatialBatchNormalization(32))
    model.add(SpatialConvolution(32, 32, 5, 5))
    model.add(ELU())
    model.add(SpatialBatchNormalization(32))
    model.add(SpatialMaxPooling(2, 2, 1, 1))
    model.add(Dropout(0.2))

    model.add(SpatialConvolution(32, 64, 5, 5))
    model.add(ELU())
    model.add(SpatialBatchNormalization(64))
    model.add(SpatialConvolution(64, 64, 5, 5))
    model.add(ELU())
    model.add(SpatialBatchNormalization(64))
    model.add(SpatialMaxPooling(2, 2, 2, 2))
    model.add(Dropout(0.3))

#    model.add(SpatialConvolution(64, 120, 5, 5))
#    model.add(ReLU())
#    model.add(SpatialMaxPooling(2, 2, 2, 2))
    model.add(SpatialConvolution(64, 128, 5, 5))
    model.add(ELU())
    model.add(SpatialBatchNormalization(128))
    model.add(SpatialConvolution(128, 256, 5, 5))
    model.add(ELU())
    model.add(SpatialBatchNormalization(256))
#    model.add(SpatialMaxPooling(1, 1, 2, 2))
    model.add(Dropout(0.4))
#    model.add(SpatialConvolution(128, 256, 5, 5, 1, 1, 1, 1))
    model.add(Reshape([128 * 2 * 2]))
    model.add(Linear(128 * 2 * 2, 84))
    model.add(ELU())
    model.add(Linear(84, class_num))
    model.add(LogSoftMax())
#    model.add(Dense(10))
    return model

def build_model_new(class_num):
    model = Sequential()
    model.add(Reshape([3, 32, 32]))
    model.add(SpatialConvolution(3, 6, 5, 5))
    model.add(Tanh())
    model.add(SpatialMaxPooling(2, 2, 1, 1))
    model.add(SpatialConvolution(6, 16, 5, 5))
    model.add(Tanh())
    model.add(SpatialMaxPooling(2, 2, 2, 2))
    model.add(SpatialConvolution(16, 120, 5, 5))
    model.add(Reshape([120 * 7 * 7]))
    model.add(Linear(120 * 7 * 7, 84))
    model.add(Tanh())
    model.add(Linear(84, class_num))
    model.add(LogSoftMax())
    return model

def build_vgg(classNum):
    model = Sequential()
    model.add(Reshape([3, 32, 32]))

    model.add(SpatialConvolution(3, 64, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(64, 64, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialMaxPooling(2, 2, 2, 2))

    model.add(SpatialConvolution(64, 128, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(128, 128, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialMaxPooling(2, 2, 2, 2))

    model.add(SpatialConvolution(128, 256, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(256, 256, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(256, 256, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialMaxPooling(2, 2, 2, 2))

    model.add(SpatialConvolution(256, 512, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(512, 512, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(512, 512, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialMaxPooling(2, 2, 2, 2))

    model.add(SpatialConvolution(512, 512, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(512, 512, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialConvolution(512, 512, 3, 3, 1, 1, 1, 1))
    model.add(ReLU(True))
    model.add(SpatialMaxPooling(2, 2, 2, 2))
    
    model.add(SpatialConvolution(512, 512, 3, 3, 1, 1, 1, 1))
    model.add(Reshape([512 * 7 * 7]))
    model.add(Linear(512 * 7 * 7, 84))
    #model.add(View(512 * 7 * 7))
   # model.add(Linear(512 * 7 * 7, 4096))
   # model.add(Threshold(0, 1e-6))
    #model.add(Linear(4096, 4096))
    #model.add(Threshold(0, 1e-6))
    model.add(Linear(4096, classNum))
    model.add(LogSoftMax())

    return model

    
def build_model_inc(class_num):
    model = Sequential()
    model.add(Reshape([3, 32, 32]))
    model.add(SpatialConvolution(3, 32, 3, 3, 1, 1, 1, 1))
    model.add(ELU())
    model.add(SpatialBatchNormalization(32))
    model.add(SpatialConvolution(32, 32, 3, 3, 1, 1, 1, 1))
    model.add(ELU())
    model.add(SpatialBatchNormalization(32))
    model.add(SpatialMaxPooling(2, 2, 1, 1))
    model.add(Dropout(0.2))

    model.add(SpatialConvolution(32, 64, 3, 3, 1, 1, 1, 1))
    model.add(ELU())
    model.add(SpatialBatchNormalization(64))
    model.add(SpatialConvolution(64, 64, 3, 3, 1, 1, 1, 1))
    model.add(ELU())
    model.add(SpatialBatchNormalization(64))
    model.add(SpatialMaxPooling(2, 2, 2, 2))
    model.add(Dropout(0.3))

    model.add(SpatialConvolution(64, 128, 3, 3, 1, 1, 1, 1))
    model.add(ELU())
    model.add(SpatialBatchNormalization(128))
    model.add(SpatialConvolution(128, 128, 3, 3, 1, 1, 1, 1))
    model.add(ELU())
    model.add(SpatialBatchNormalization(128))
    model.add(SpatialMaxPooling(2, 2, 2, 2))
    model.add(Dropout(0.4))

#    model.add(SpatialConvolution(128, 256, 3, 3, 1, 1, 1, 1))
    model.add(Reshape([128 * 7 * 7]))
    model.add(Linear(128 * 7 * 7, 84))
    model.add(ELU())
    model.add(Linear(84, class_num))
    model.add(SoftMax())
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

    sc = SparkContext(appName=options.appName, conf=create_spark_conf())

    redire_spark_logs()
    show_bigdl_info_logs()
    init_engine()

    learning_rate=float(options.learningRate)
    learning_rate_decay=float(options.learningrateDecay)

    (train_images, train_labels), (test_images, test_labels) = cifar100.load_data()
    training_mean = np.mean(train_images)
    training_std = np.std(train_images)
    test_mean = np.mean(test_images)
    test_std = np.std(test_images)

    images = sc.parallelize(train_images)
    labels = sc.parallelize(train_labels+1)
    record = images.zip(labels)
    train_data = record.map(lambda rec_tuple: (normalizer(rec_tuple[0], training_mean, training_std), rec_tuple[1])).map(lambda t: Sample.from_ndarray(t[0], t[1]))

    images = sc.parallelize(test_images)
    labels = sc.parallelize(test_labels+1)
    record = images.zip(labels)
    test_data = record.map(lambda rec_tuple: (normalizer(rec_tuple[0], test_mean, test_std), rec_tuple[1])).map(lambda t: Sample.from_ndarray(t[0], t[1]))

    optimizer = Optimizer(
        model=build_model_new(100),
        training_rdd=train_data,
        criterion=ClassNLLCriterion(),
        optim_method=RMSprop(learningrate=learning_rate, learningrate_decay=learning_rate_decay),#, momentum=0.9, dampening=0.0, nesterov=True),
        end_trigger=MaxEpoch(int(options.endTriggerNum)),
        batch_size=options.batchSize)

    validate_optimizer(optimizer, test_data)
    trained_model = optimizer.optimize()
    parameters = trained_model.parameters()
