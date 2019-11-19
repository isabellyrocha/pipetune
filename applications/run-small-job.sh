#!/bin/bash

/usr/local/spark/bin/spark-submit \
	--master spark://eiger-1.maas:7077 \
	--driver-memory 2G \
	--total-executor-cores 8 \
	--executor-cores 4 \
	--executor-memory 2G \
	--py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/bigdl/models/lenet5.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/bigdl/models/lenet5.py \
	--action train \
	--dataPath /home/ubuntu/dataset/mnist/ \
	--batchSize 512 \
	--learningRate 0.01 \
	--learningrateDecay 0.0002 \
	--endTriggerNum 16
