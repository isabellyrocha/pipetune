#!/bin/bash

spark-submit \
	--master spark://eiger-1.maas:7077 \
	--driver-memory 2G \
	--total-executor-cores $2 \
	--executor-cores 8 \
	--executor-memory 4G \
	--py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/sprinting/applications/cifar10.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/sprinting/applications/cifar10.py \
	--appName $1 \
	--action train \
	--batchSize $3 \
	--learningRate 0.01 \
	--learningrateDecay 0.0002 \
	--endTriggerNum $4
