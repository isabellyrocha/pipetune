spark-submit \
	--master spark://eiger-1.maas:7077 \
	--driver-memory 16G \
	--executor-memory 16G \
        --executor-cores 4 \
	--total-executor-cores 16 \
	--class com.intel.analytics.bigdl.models.vgg.Train \
	/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar \
	-f /home/ubuntu/cifar10 \
	-b 32 \
	--summary ./log \
	--checkpoint ./model
