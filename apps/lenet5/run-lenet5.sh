#!/bin/bash

MASTER=spark://<master>:7077

spark-submit \
	--master $MASTER \
	--name mnist \
	--driver-memory 16G \
	--total-executor-cores $1 \
	--executor-cores $2 \
	--executor-memory $3G \
	--py-files $HOME/BigDL/dist/lib/bigdl-0.12.0-SNAPSHOT-python-api.zip,$HOME/pipetune/apps/lenet5/lenet5.py \
	--properties-file $HOME/BigDL/dist/conf/spark-bigdl.conf \
	--jars $HOME/BigDL/dist/lib/bigdl-0.12.0-SNAPSHOT-jar-with-dependencies.jar \
        --conf spark.dynamicAllocation.enabled=false \
	--conf spark.driver.extraClassPath=$HOME/BigDL/dist/lib/bigdl-0.12.0-SNAPSHOT-jar-with-dependencies.jar \
	--conf spark.executer.extraClassPath=bigdl-0.12.0-SNAPSHOT-jar-with-dependencies.jar $HOME/pipetune/apps/lenet5/lenet5.py \
	--appName mnist \
	--action train \
	--dataPath /tmp/$4 \
	--batchSize $5 \
	--learningRate 0.0781816 \
	--learningrateDecay 0.0905019 \
	--endTriggerNum 1
