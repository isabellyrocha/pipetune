# PipeTune

> A pipelined paralelism approch for hyper and system parameter tuning.

---

## Table of Contents

- [Deployment](#deployment)
- [BigDL] (#bigdl)

---

## Deployment

> Spark 2.4.1 Standalone Cluster Deployment

### Requirements

- Java 1.8.0

### Download and Install

> Install Java 1.8.0

```Shell
$ apt-get install openjdk-8-jdk
$ apt-get install openjdk-8-jre
```

> Install Spark 2.4.1

```Shell
$ cd /usr/local
$ wget https://archive.apache.org/dist/spark/spark-2.4.1/spark-2.4.1-bin-hadoop2.7.tgz
$ tar -xzf spark-2.4.1-bin-hadoop2.7.tgz
$ echo "export PATH=$PATH:/usr/local/spark-2.4.1-bin-hadoop2.7/bin" >> $HOME/.bashrc
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

## BigDL

> BigDL is a distributed deep learning library for Apache Spark.

### Requirements

- Spark
- Maven
- Python

### Download and Install



---
