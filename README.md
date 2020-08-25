<p align="center"><img src="https://github.com/isabellyrocha/pipetune/blob/master/documentation/pipetune.png" /></p>

PipeTune implements a pipelined paralelism approach for hyper and system parameter tuning.

---

## Table of Contents

- [Deploy Spark Cluster](#spark.deployment)
- [BigDL Setup](#bigdl.setup)
- [Power Measurements Setup](#power.measurements)

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

![alt text](https://github.com/isabellyrocha/pipetune/raw/master/documentation/spark_master_web.png?raw=true)

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

![alt text](https://github.com/isabellyrocha/pipetune/blob/master/documentation/bigdl_test.gif?raw=true)

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
