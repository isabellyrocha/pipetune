#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from optparse import OptionParser
from bigdl.models.lenet.utils import *
from bigdl.dataset.transformer import *
from bigdl.nn.layer import *
from bigdl.nn.criterion import *
from bigdl.optim.optimizer import *
from bigdl.util.common import *
import utils
import mnist
import os

def build_model(class_num):
    model = Sequential()
    model.add(Reshape([1, 28, 28]))
    model.add(SpatialConvolution(1, 6, 5, 5))
    model.add(Tanh())
    model.add(SpatialMaxPooling(2, 2, 1, 1))
    model.add(SpatialConvolution(6, 16, 5, 5))
    model.add(Tanh())
    model.add(SpatialMaxPooling(2, 2, 2, 2))
    model.add(SpatialConvolution(16, 120, 5, 5))
    model.add(Reshape([120 * 5 * 5]))
    model.add(Linear(120 * 5 * 5, 84))
    model.add(Tanh())
    model.add(Linear(84, class_num))
    model.add(LogSoftMax())
    return model

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--appName", dest="appName",default="lenet5")
    parser.add_option("-a", "--action", dest="action", default="train")
    parser.add_option("-b", "--batchSize", type=int, dest="batchSize", default="128")
    parser.add_option("-o", "--modelPath", dest="modelPath", default="/tmp/lenet5/model.test")
    parser.add_option("-c", "--checkpointPath", dest="checkpointPath", default="/tmp/lenet5")
    parser.add_option("-t", "--endTriggerType", dest="endTriggerType", default="epoch")
    parser.add_option("-n", "--endTriggerNum", type=int, dest="endTriggerNum", default="20")
    parser.add_option("-d", "--dataPath", dest="dataPath", default="/tmp/mnist")
    parser.add_option("-l", "--learningRate", dest="learningRate", default="0.01")
    parser.add_option("-k", "--learningrateDecay", dest="learningrateDecay", default="0.0002")
    parser.add_option("-j", "--executorCores", dest="executorCores", default="1")
    (options, args) = parser.parse_args(sys.argv)

    sc = SparkContext(appName=options.appName, conf=create_spark_conf())
    redire_spark_logs()
    show_bigdl_info_logs()
    init_engine()
    learning_rate=float(options.learningRate)
    learning_rate_decay=float(options.learningrateDecay)
    print(learning_rate)
    if options.action == "train":
        #(train_data, test_data) = preprocess_mnist(sc, options)
        (train_data, test_data) = utils.get_mnist_costum(sc, options.dataPath)
        if False: #os.path.exists("/tmp/%s.bigdl" % options.appName):
            model = Model.loadModel("/tmp/%s.bigdl" % options.appName, "/tmp/%s.bin" % options.appName)
        else:
            model = build_model(10)
        optimizer = Optimizer(
            model=model,
            training_rdd=train_data,
            criterion=ClassNLLCriterion(),
            optim_method=SGD(learningrate=learning_rate, learningrate_decay=learning_rate_decay, momentum=0.9, dampening=0.0, nesterov=True),
            end_trigger=get_end_trigger(options),
            batch_size=options.batchSize)
        validate_optimizer(optimizer, test_data, options)
        trained_model = optimizer.optimize()
        parameters = trained_model.parameters()
#        trained_model.saveModel("/tmp/%s.bigdl" % options.appName, "/tmp/%s.bin" % options.appName, True)
    elif options.action == "test":
        # Load a pre-trained model and then validate it through top1 accuracy.
        test_data = get_mnist(sc, "test", options.dataPath) \
            .map(lambda rec_tuple: (normalizer(rec_tuple[0], cifar10.TEST_MEAN, cifar10.TEST_STD),
                                    rec_tuple[1])) \
            .map(lambda t: Sample.from_ndarray(t[0], t[1]))
        model = Model.load(options.modelPath)
        results = model.evaluate(test_data, options.batchSize, [Top1Accuracy()])
        for result in results:
            print(result)
    sc.stop()
