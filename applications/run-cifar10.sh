#!/bin/bash

spark-submit \
	--master spark://eiger-1.maas:7077 \
	--driver-memory 16G \
	--executor-memory 16G \
	--total-executor-cores $2 \
	--executor-cores 1 \
	--py-files /home/ubuntu/bigdl/lib/bigdl-custom.zip,/home/ubuntu/pipetune/applications/cifar10.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/pipetune/applications/cifar10.py \
	--appName $1 \
	--action train \
	--batchSize $3 \
	--learningRate 0.01 \
	--learningrateDecay 0.0002 \
	--endTriggerNum $4
