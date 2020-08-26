#!/bin/bash

spark-submit \
	--master spark://eiger-1.maas:7077 \
	--driver-memory 32G \
	--total-executor-cores $1 \
	--executor-cores $2 \
	--executor-memory $3G \
	--py-files $HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-python-api.zip,$HOME/pipetune/applications/news20/textclassifier.py \
	--properties-file $HOME/BigDL/dist/conf/spark-bigdl.conf \
	--jars $HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=$HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar $HOME/pipetune/applications/news20/textclassifier.py \
        --appName news20 \
	--model $4 \
	--maxEpoch 1 \
	--batchSize $5 \
	--embeddingDim 200 \
	--learningRate 0.05
