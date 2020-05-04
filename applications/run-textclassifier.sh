#!/bin/bash

spark-submit \
	--master spark://eiger-1.maas:7078 \
	--driver-memory 32G \
	--total-executor-cores 16 \
	--executor-cores 4 \
	--executor-memory 32G \
	--py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/pipetune/applications/textclassifier.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/pipetune/applications/textclassifier.py \
	--model cnn \
	--max_epoch 1 \
	--batchSize 64 \
	--embedding_dim 200
	--learning_rate 0.05
