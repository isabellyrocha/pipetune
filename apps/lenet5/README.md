# LeNet5 Model on MNIST or FASHION-MNIST

LeNet5 is a classical CNN model used in digital number classification. For more detailed information, please refer to <http://yann.lecun.com/exdb/lenet/>. This application is an extension of the [LeNet5 example](https://github.com/intel-analytics/BigDL/tree/master/pyspark/bigdl/models/lenet) available from the official BigDL documentation. This application slightly **modifies the model** itsel, **automatically retrieves previously trained model** if any, **adds support to the fashion-mnist dataset**, and **extends the list of hyperparameters** which can be chosen by the user.

## MNIST

MNIST is a dataset consisting of handwritten digits images. More information in <http://yann.lecun.com/exdb/mnist/>.

## FASHION-MNIST

FASHION-MNIST is a dataset of Zalando's article images. More information in <https://github.com/zalandoresearch/fashion-mnist>.

## Install dependencies
 * [Install dependencies](../../README.md#install.bigdl.dependencies)

## How to run this example:
- Please note that due to permission issues, this example **cannot** run on Windows.
- Program automaticaly downloads the chosen dataset if not yet available in the specified `dataPath`.
- Program assumes `BigDL` to have been installed in `$HOME` directory
- Program assumes `pipetune` respository to have been cloned to `$HOME` directory.

The LeNet model can be trained in Spark local mode with the following command, or it can be distributed across a cluster by modifying the Spark master.

- You can run it using the script `run-lenet5.sh`. Please update the variable `MASTER` in the script header with your Spark master address. Find below one example of how to run the script with a sample input:
```{engine='sh'}
./run-news20.sh 4 1 4 mnist 32
```

- Alternativaly, you can run the application directly via spark interface.

```{engine='sh'}
MASTER=local[*]
spark-submit \
	--master $MASTER \
	--name mnist \
	--driver-memory 16G \
	--total-executor-cores 32 \
	--executor-cores 1 \
	--executor-memory 2G \
	--py-files $HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-python-api.zip,$HOME/pipetune/apps/lenet5/lenet5.py \
	--properties-file $HOME/BigDL/dist/conf/spark-bigdl.conf \
	--jars $HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=$HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar $HOME/pipetune/apps/lenet5/lenet5.py \
	--appName mnist \
	--action train \
	--dataPath /tmp/mnist \
	--batchSize 256 \
	--learningRate 0.01 \
	--learningrateDecay 0.001 \
	--endTriggerNum 10
 ```

* `--total-executor-cores` defines the maximum number of cores used by the application.
* `--executor-cores` defines the numeber of cores each executer has. Note that the number of executers is indirectly defined by the ration `total-executor-cores` to `executor-cores`.
* `--action` it can be train or test.
* `--dataPath` option can be used to set the path for downloading data, the default value is `/tmp/mnist`. If `/tmp/fashion_mnist` is used then the `fashion-mnist` will be used/downloaded. Make sure that you have write permission to the specified path. 
* `--batchSize` option can be used to set batch size, the default value is 128.
* `--endTriggerType` option can be used to control how to end the training process, the value can be "epoch" or "iteration" and default value is "epoch".
* `--endTriggerNum` use together with `endTriggerType`, the default value is 20.
* `--modelPath` option can be used to set model path for testing, the default value is /tmp/`appName`.bigdl.
* `--checkpointPath` option can be used to set checkpoint path for saving model, the default value is /tmp/lenet5/.
* `--optimizerVersion` option can be used to set DistriOptimizer version, the value can be "optimizerV1" or "optimizerV2".
* `--momentum` option can be used to set mementum, the default value is 0.9.
* `--dampening` option can be used to set dampening, the default value is 0.0.
* `--nesterov` option can be used to set nesterov, the default value is True.

To verify the accuracy, search "accuracy" from log:

```
INFO  DistriOptimizer$:247 - [Epoch 1 0/60000][Iteration 1][Wall Clock 0.0s] Train 128 in xx seconds. Throughput is xx records/second.
INFO  DistriOptimizer$:522 - Top1Accuracy is Accuracy(correct: 9572, count: 10000, accuracy: 0.9572)
```
