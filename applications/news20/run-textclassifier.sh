#!/bin/bash

spark-submit \
	--master spark://eiger-1.maas:7077 \
	--driver-memory 32G \
	--total-executor-cores $1 \
	--executor-cores $2 \
	--executor-memory $3G \
	--py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/pipetune/applications/textclassifier.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/pipetune/applications/textclassifier.py \
	--model $4 \
	--max_epoch 5 \
	--batchSize $5 \
	--embedding_dim 200 \
	--learning_rate 0.05
