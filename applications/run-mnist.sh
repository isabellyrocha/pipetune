#!/bin/bash

spark-submit \
	--master k8s://https://172.28.1.76:6443 \
	--deploy-mode cluster \
	--name test \
	--py-files /home/ubuntu/bigdl/lib/bigdl-0.8.0-python-api.zip,/home/ubuntu/pipetune/applications/lenet5.py \
	--properties-file /home/ubuntu/bigdl/conf/spark-bigdl.conf \
	--jars /home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.kubernetes.namespace=spark \
	--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark-sa \
	--conf spark.executor.instances=2 \
	--conf spark.kubernetes.container.image.pullPolicy=Always \
        --conf spark.kubernetes.container.image=lightbend/spark:2.0.1-OpenShift-2.4.0-rh \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar /home/ubuntu/pipetune/applications/lenet5.py \
	--action train \
	--dataPath /home/ubuntu/dataset/mnist/ \
	--batchSize 1024 \
	--learningRate 0.01 \
	--learningrateDecay 0.0002 \
	--endTriggerNum 1
