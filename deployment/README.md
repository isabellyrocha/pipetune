# Spark 2.4.1 Standalone Cluster Deployment

## Requirements

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

### Deploy Master Node

```Shell
$ cd /usr/local/spark-2.4.1-bin-hadoop2.7
$ ./sbin/start-master.sh
```

### Add Workers to Cluster

```Shell
$ cd /usr/local/spark-2.4.1-bin-hadoop2.7
$ ./sbin/start-slave.sh <master-spark-URL>
```
