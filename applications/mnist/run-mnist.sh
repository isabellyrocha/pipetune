#!/bin/bash

spark-submit \
	--master spark://eiger-1.maas:7077 \
	--name mnist \
	--driver-memory 16G \
	--total-executor-cores $1 \
	--executor-cores $2 \
	--executor-memory $3G \
	--py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/pipetune/applications/mnist/lenet5.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/pipetune/applications/mnist/lenet5.py \
	--appName mnist \
	--action train \
	--dataPath /home/ubuntu/dataset/$4 \
	--batchSize $5 \
	--learningRate 0.01 \
	--learningrateDecay 0.0002 \
	--endTriggerNum 10
