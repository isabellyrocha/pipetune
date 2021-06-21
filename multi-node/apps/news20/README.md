# CNN, GRU or LSTM Models on News20 Dataset

CNN, LSTM or GRU text classification models on a 20 Newsgroup dataset with 20 different categories. 
For more detailed information, please refer to <https://blog.keras.io/using-pre-trained-word-embeddings-in-a-keras-model.html>. 
This application is an extension of the [textclassifier example](https://github.com/intel-analytics/BigDL/tree/master/pyspark/bigdl/models/textclassifier) 
available in the official BigDL documentation. This application slightly **modifies the models** themselves, 
**automatically retrieves previously trained model** if any, and **extends the list of hyperparameters** which can be chosen by the user.

## Install dependencies
 * [Install dependencies](../../README.md#install.bigdl.dependencies)

## How to run this example:
- Please note that due to permission issues, this example **cannot** run on Windows.
- Program automaticaly downloads the chosen dataset if not yet available in the specified `dataPath`.
- Program assumes `BigDL` to have been installed in `$HOME` directory
- Program assumes `pipetune` respository to have been cloned to `$HOME` directory.

The models can be trained in Spark local mode with the following command, or it can be distributed across a cluster by modifying the Spark master.

- You can run it using the script `run-lenet5.sh`. Please update the variable `MASTER` in the script header with your Spark master address. Find below one example of how to run the script with a sample input:
```{engine='sh'}
./run-news20.sh 4 1 4 cnn 32
```

- Alternativaly, you can run the application directly via spark interface.
```{engine='sh'}
MASTER=local[*]
spark-submit \
	--master $MASTER \
	--driver-memory 32G \
	--total-executor-cores 32 \
	--executor-cores 8 \
	--executor-memory 8G \
	--py-files $HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-python-api.zip,$HOME/pipetune/applications/news20/textclassifier.py \
	--properties-file $HOME/BigDL/dist/conf/spark-bigdl.conf \
	--jars $HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=$HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar $HOME/pipetune/applications/news20/textclassifier.py \
        --appName news20 \
	--model cnn \
	--maxEpoch 1 \
	--batchSize 1024 \
	--embeddingDim 200 \
	--learningRate 0.05
 ```

* `--total-executor-cores` defines the maximum number of cores used by the application.
* `--executor-cores` defines the numeber of cores each executer has. Note that the number of executers is indirectly defined by the ration `total-executor-cores to `--executor-cores`.
* `--action` can be train or test.
* `--appName` defines the name of the application, which also defined the name of the saved model.
* `--dataPath` option can be used to set the path for downloading news20 data, the default value is /tmp/news20. Make sure that you have write permission to the specified path.
* `--maxEpoch` option can be used to set how many epochs the model to be trained, the default value is 30.
* `--model` option can be used to choose a model to be trained, three models are supported in this example,
which are `cnn`, `lstm` and `gru`, default is `cnn`.
* `--batchSize` option can be used to set batch size, the default value is 128.
* `--embeddingDim` option can be used to set the embedding size of word vector, the default value is 200.
* `--learningRate` option can be used to set learning rate, default is 0.05.
* `--learningRateDecay` option can be used to set learning rate decay, default is 0.01.
* `--optimizerVersion` option can be used to set DistriOptimizer version, the value can be "optimizerV1" or "optimizerV2".
* `--sequenceLen` option can be used to set the sequence length, default is 500.
* `--maxWords` option can be used to set the max words, default is 5000.
* `--trainSplit` option can be used to set the train split, default is 0.8.


To verify the accuracy, search "accuracy" from log:

```
INFO  DistriOptimizer$:247 - [Epoch 1 0/60000][Iteration 1][Wall Clock 0.0s] Train 128 in xx seconds. Throughput is xx records/second.
INFO  DistriOptimizer$:522 - Top1Accuracy is Accuracy(correct: 9572, count: 10000, accuracy: 0.9572)
```
