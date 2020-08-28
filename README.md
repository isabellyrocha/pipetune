<p align="center"><img src="https://github.com/isabellyrocha/pipetune/blob/master/docs/pipetune.png" /></p>

PipeTune implements a pipelined paralelism approach for hyper and system parameter tuning.

---

## Table of Contents

- [Deploy Spark Cluster](#spark.deployment)
- [BigDL Setup](#bigdl.setup)
- [Power Measurements Setup](#power.measurements)
- [Clustering](#clustering)

---

<a name="spark.deployment"></a>
## Deploy Spark Cluster

> Spark 2.4.1 Standalone Cluster Deployment.

### Requirements

- Java 1.8.0

### Download and Install

> Install Java 1.8.0.

```Shell
$ apt-get install openjdk-8-jdk
$ apt-get install openjdk-8-jre
```

> Install Spark 2.4.1.

```Shell
$ cd /usr/local
$ wget https://archive.apache.org/dist/spark/spark-2.4.1/spark-2.4.1-bin-hadoop2.7.tgz
$ tar -xzf spark-2.4.1-bin-hadoop2.7.tgz
$ echo "export PATH=$PATH:/usr/local/spark-2.4.1-bin-hadoop2.7/bin" >> $HOME/.bashrc
$ source .bashrc
```

### Set Environment Variables

> Use Spark's template `spark-env.sh.template`

```Shell
$ cp conf/spark-env.sh.template conf/spark-env.sh
```

> Copy the following configurations into `spark-env.sh`

```
export SPARK_WORKER_INSTANCES=1
export SPARK_WORKER_MEMORY=32g
export SPARK_WORKER_CORES=8
```

### Deploy Master Node

```Shell
$ cd /usr/local/spark-2.4.1-bin-hadoop2.7
$ ./sbin/start-master.sh
```

### Add Worker Nodes to Cluster

```Shell
$ cd /usr/local/spark-2.4.1-bin-hadoop2.7
$ ./sbin/start-slave.sh <master-spark-URL>
```

### Accessing MasterWebUI

- MasterWebUI abailable at: `http://masternode:8080`

![alt text](https://github.com/isabellyrocha/pipetune/raw/master/docs/spark_master_web.png?raw=true)

---

<a name="bigdl.setup"></a>
## BigDL Setup

> BigDL is a distributed deep learning library for Apache Spark.

### Requirements

- Spark
- Maven
- Python

<a name="install.bigdl.dependencies"></a>
### Download and Install

> Install requirements.
```Shell
$ sudo apt install maven
$ sudo apt-get install python
$ sudo apt install python-pip
$ echo "export LC_ALL="en_US.UTF-8"" >> .bashrc
$ echo "export LC_CTYPE="en_US.UTF-8"" >> .bashrc
$ source .bashrc
```

> Install Python dependencies on master and each worker node.
```Shell
$ pip install six numpy
$ pip install --upgrade pip
$ pip install BigDL==0.10.0     # for Python 2.7
$ pip3 install BigDL==0.10.0    # for Python 3.5 and Python 3.6
```

> Download and install BigDL.

```Shell
$ git clone https://github.com/intel-analytics/BigDL.git
$ cd BigDL
$ ./make-dist.sh -P spark_2.x
```
### Test BigDL

- Test BiglDL with one of the applications avalable in `pipetune/applications`
- For more details on the applications refer to [Lenet5](https://github.com/isabellyrocha/pipetune/tree/master/applications/lenet5) or [News20](https://github.com/isabellyrocha/pipetune/tree/master/applications/news20).

![alt text](https://github.com/isabellyrocha/pipetune/blob/master/docs/bigdl_test.gif?raw=true)

### BigDL Config file

Once the BigDL application is tested a config file describing it has to be created.
This file will be used by the BigDL Python module which is part of PipeTune.
Below is an exemple of how this file should look like and a list describing each item.
Similar examples can be found in `bigdl/confif`.

- `master` especifies Spark's master address
- `driver_memory` espeficies the default memory to be used by the driver
- `total_executor_cores` espeficies the default total executeor cores (has to be a multiple of `executor_cores`)
- `executor_cores` espeficies the number of cores which should be assigned to each executor 
- `executor_memory` esfeficies the default memory to be used by each executor
- `py_files` lists the needed python files for the application
- `properties_file` points to a config file containging Spark and BigDL configurations
- `jars` points to the jar file with all the needed BigDL dependencies
- `conf` points to the python file containing the model implementation
- `extra` described all the prameters which as especific for the application itself.

```yaml
{
    "master": "spark://eiger-1.maas:7077",
    "driver_memory": "2G",
    "total_executor_cores": "1",
    "executor_cores": "1",
    "executor_memory": "2G",
    "py_files": "/home/ubuntu/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-python-api.zip,/home/ubuntu/pipetune/apps/lenet5/lenet5_pure.py",
    "properties_file": "/home/ubuntu/BigDL/dist/conf/spark-bigdl.conf",
    "jars": "/home/ubuntu/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar",
    "conf": "/home/ubuntu/pipetune/apps/lenet5/lenet5_pure.py",
    "extras": {
        "action": "train",
        "dataPath": "/home/ubuntu/dataset/mnist",
        "batchSize": "32",
        "learningRate": "0.01",
        "learningrateDecay": "0.0002",
        "endTriggerNum": "1"
    }
}
```

---
<a name="power.measurements"></a>
## Power Measurements Setup
> Settig up cluster's power metrics for energy reports.

### Requirements

- PDU (if PDU is not available, metrics can be collected using PCM)
- InfluxDB

### Download and Install
> The following steps are only required when PCM is needed (in each cluster node).
```Shell
$ git clone https://github.com/opcm/pcm.git
$ cd pcm
$ make
$ sudo modprobe msr
```

> Installing and setting up the time series database.
```Shell
$ sudo apt install influxdb
$ service influxdb start
$ influx
$ CREATE DATABASE energy
```

> Initiate power metrics collection.
```Shell
$ # PDU
$ nohup python3 $HOME/pipetune/monitoring/pdu_power.py <http://pdu-address> 1 &
$ # PCM 
$ # Following step required only in master node
$ mkdir $HOME/pcm_data
$ # Following steps required in each cluster node
$ nohup ssh <nodename> sudo ./pcm/pcm.x /csv > $HOME/pcm_data/<nodename>.log &
$ nohup python3 $HOME/pipetune/monitoring/pcm_power.py $HOME/pcm_data/<nodename>.log <nodename> &
```
---
### Clustering

In the current version, clustring is implemented using Kmeans algorithm on low level events collected using hardware performance counters. A preselected list of 58 performance counters are collected every second during a given epoch and the system configurations to be applied in that given trial is deficed by this profile. A model is pretrainined in available at ``, but the model is updated as new workloads comes to the system. Bellow we can see a subset of the profiling results for a given workloads during 5 epochs.

![alt text](https://github.com/isabellyrocha/pipetune/blob/master/docs/profiling.png?raw=true)

> Install perf in those nodes where profiling is needed

```Shell
$ sudo apt install linux-tools-common linux-tools-4.4.0-184-generic linux-cloud-tools-4.4.0-184-generic
```

> Create a directory where all the collected data will be saved

```Shell
$ mkdir $HOME/perf
```
