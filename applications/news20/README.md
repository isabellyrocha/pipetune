# CNN, GRU or LSTM Models on News20 Dataset

CNN, LSTM or GRU text classification models on a 20 Newsgroup dataset with 20 different categories. 
For more detailed information, please refer to <https://blog.keras.io/using-pre-trained-word-embeddings-in-a-keras-model.html>. 
This application is an extension of the [textclassifier example](https://github.com/intel-analytics/BigDL/tree/master/pyspark/bigdl/models/textclassifier) 
available in the official BigDL documentation. This application slightly **modifies the models** themselves, 
**automatically retrieves previously trained model** if any, and **extends the list of hyperparameters** which can be chosen by the user.

## Install dependencies
 * [Install dependencies](../../README.md#install.bigdl.dependencies)

## How to run this example:
- Please note that due to some permission issue, this example **cannot** be run on Windows.
- Program automaticaly downloads the chosen dataset if not yet available in the specified `dataPath`.

The models can be trained in Spark local mode with the following command, or it can be distributed across a cluster by modifying the Spark master.

```{r, engine='sh'}
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

* `--data_path` option can be used to set the path for downloading news20 data, the default value is /tmp/news20. Make sure that you have write permission to the specified path.
* `--max_epoch` option can be used to set how many epochs the model to be trained
* `--model` option can be used to choose a model to be trained, three models are supported in this example,
which are `cnn`, `lstm` and `gru`, default is `cnn`
* `--batchSize` option can be used to set batch size, the default value is 128
* `--embedding_dim` option can be used to set the embedding size of word vector, the default value is 200.
* `--learning_rate` option can be used to set learning rate, default is 0.05.
* `--optimizerVersion` option can be used to set DistriOptimizer version, the value can be "optimizerV1" or "optimizerV2".

To verify the accuracy, search "accuracy" from log:

```
INFO  DistriOptimizer$:247 - [Epoch 1 0/60000][Iteration 1][Wall Clock 0.0s] Train 128 in xx seconds. Throughput is xx records/second.
INFO  DistriOptimizer$:522 - Top1Accuracy is Accuracy(correct: 9572, count: 10000, accuracy: 0.9572)
```
