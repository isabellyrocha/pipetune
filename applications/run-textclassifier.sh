#!/bin/bash

spark-submit \
	--master k8s://https://172.28.1.76:6443 \
	--deploy-mode cluster \
	--name text-test \
	--driver-memory 32G \
	--total-executor-cores 16 \
	--executor-cores 4 \
	--executor-memory 32G \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
        --py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/pipetune/applications/textclassifier.py \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/pipetune/applications/textclassifier.py 
