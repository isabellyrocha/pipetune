<p align="center"><img src="https://github.com/isabellyrocha/pipetune/blob/master/docs/logo.png"/></p>

PipeTune implements a pipelined paralelism approach for hyper and system parameter tuning. This repository contains the following two versions of this implementation: 
1. [Single-node version](#single): implemented in Python on top of tensorflow. 
2. [Multi-node version](#multi): implemented in Python on top of BigDL.

These two versions are independet from each other but implement the same principles introduced py PipeTune's algorithm.

---
<a name="single"></a>
## Walkthrough Single-Node Version

- [System Requirements](#sys.requirements)
- [Python Environment](#environment)
- [Input Data](#input.data)
- [Running Offline Tuning Experiments](#online)
- [Running Online Tuning Experiments](#offline)

<a name="sys.requirements"></a>
## System Requirements

- INTEL RAPL enabled CPU and Linux Kernel
- CPU with at least 8 cores (since we have not parameterize this input)

<a name="environment"></a>
## Python Environment

- Python 3
- Install pipenv

```Shell
$ cd single-node-setup                                                                                            
$ pipenv sync                                                        
```

<a name="input.data"></a>
## Input Data

- BFS
- Jacobi
- Kmeans
- NN
- Spark Kmeans
- Spark Stream

> The input data is formatted in h5py. The binaries are not uploaded to this repository because of Github's file size limitation. You will be directed in the following instructions to download them from google drive. The link below is direct access to the binaries.

https://drive.google.com/file/d/1xCeRtvwoXu7X4iOYKi7m7iaItk88j0mT/view?usp=sharing


> PIPETUNE is an optimized version of our V2 implementation. It only tunes jobs it sees for the first time. Recurring jobs are quickly profiled and classified by kmeans.Jobs exhibiting similar profiles are assigned parameters considered ideal for profiles seen in the past. Many tuning trials are bypassed so that a good trained model can complete quickly. Accurate classification means recurring jobs experience 1 tuning trial plus training. The single-node-setup uses the V2 results to compute PIPETUNE's results.

<a name="online"></a>
## Running Offline Tuning Experiments
> Navigate to the single-node-setup/offline directory

> Run experiments for V1 implementation.
```Shell
$ pipenv run gdown --id 1xCeRtvwoXu7X4iOYKi7m7iaItk88j0mT --output jobs.zip
$ unzip jobs.zip
$ pipenv run python offline_tuning_exp_v1.py
```

> Run experiments for V2 implementation.
```Shell
$ pipenv run python offline_tuning_exp_v2.py
```

<a name="offline"></a>
## Running Online Tuning Experiments
> Navigate to the single-node-setup/online directory.

> Run experiments for V1 implementation.
```Shell
$ pipenv run gdown --id 1xCeRtvwoXu7X4iOYKi7m7iaItk88j0mT --output jobs.zip
$ unzip jobs.zip
$ pipenv run python online_tuning_exp_v1.py
```

> Run experiments for V2 implementation.
```Shell
$ pipenv run python online_tuning_exp_v2.py
```

---
<a name="multi"></a>
## Walkthrough Multi-Node Version

- [Deploy Spark Cluster](#spark.deployment)
- [BigDL Setup](#bigdl.setup)
- [Power Measurements Setup](#power.measurements)
- [Clustering](#clustering)
- [PipeTune](#pipetune)

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
$ source $HOME/.bashrc
```

### Set Environment Variables

> Use Spark's template `spark-env.sh.template`

```Shell
$ cd spark-2.4.1-bin-hadoop2.7/
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
$ ./sbin/start-slave.sh spark://<master-host>:7077
```

Note: If you get connection refused when adding the workers, comment out the `127.0.0.1 *` lines in `/etc/hosts`.

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
$ echo "export LC_ALL="en_US.UTF-8"" >> .bashrc
$ echo "export LC_CTYPE="en_US.UTF-8"" >> .bashrc
$ source .bashrc
```

> Install Python dependencies on master and each worker node.
```Shell
$ sudo apt install python-pip
# For Ubuntu 20.04 pip for Python 2 is not included in repositories.
# So you need to install pip for Python 2 using the get-pip.py script.
$ curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py 
$ sudo python2 get-pip.py
# Make sure to install the dependencies from a root account (sudo does not suffice).
$ pip install six numpy
$ pip install --upgrade pip
$ pip install BigDL==0.10.0 
```

> Download and install BigDL.

```Shell
$ git clone https://github.com/intel-analytics/BigDL.git
$ cd BigDL
$ ./make-dist.sh -P spark_2.x
```
### Test BigDL

- Test BiglDL with one of the applications avalable in `pipetune/apps`
- For more details on the applications refer to [Lenet5](https://github.com/isabellyrocha/pipetune/tree/master/apps/lenet5) or [News20](https://github.com/isabellyrocha/pipetune/tree/master/apps/news20).

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
- `extra` describes all the prameters which as especific for the application itself.

```yaml
{
    "master": "spark://eiger-1.maas:7077",
    "driver_memory": "2G",
    "total_executor_cores": "1",
    "executor_cores": "1",
    "executor_memory": "2G",
    "py_files": "$HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-python-api.zip,apps/lenet5/lenet5_pure.py",
    "properties_file": "$HOME/BigDL/dist/conf/spark-bigdl.conf",
    "jars": "$HOME/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar",
    "conf": "apps/lenet5/lenet5_pure.py",
    "extras": {
        "action": "train",
        "dataPath": "$HOME/dataset/mnist",
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

> Test if the metrics are being fetched to the database
```Shell
$ influx
$ use energy
$ SELECT * FROM "pdu_power/node_utilization" WHERE time > now() - 1m AND  nodename = 'yournodename' # If you're using PDU
$ SELECT * FROM "pcm_power/node_utilization" WHERE time > now() - 1m AND  nodename = 'yournodename' # If you're using PDM
```

---
### Clustering

In the current version, clustring is implemented using Kmeans algorithm on low level events collected using hardware performance counters. A preselected list of 58 performance counters are collected every second during a given epoch and the system configurations to be applied in that given trial is defined by this profile. A pretrainined model is available at `clustering/model.pkl`, but the model is updated as new workloads comes to the system. Bellow we can see a subset of the profiling results for a given workloads during 5 epochs.

![alt text](https://github.com/isabellyrocha/pipetune/blob/master/docs/probing.png?raw=true)

> Install perf in those nodes where profiling is needed

```Shell
$ sudo apt install linux-tools-common linux-tools-generic linux-cloud-tools-generic
```

> Create a directory where all the collected data will be saved

```Shell
$ mkdir $HOME/perf
```

---

<a name="pipetune"></a>
## PipeTune

> Install dependencies
```Shell
$ pip3 install ray dataclasses influxdb paramiko scp tensorboardx
```

> Create BigDL logging directory
```Shell
$ mkdir $HOME/bigdl_logs
```

If all the previous steps were perfomed correctly, we can now finally run PipeTune.

You can test PipeTune itself by running the following script which uses an already condifgured file for tuning a LENET model with the MNIST dataset. Please note that this script assumes that you have tested the application individually. In the first time you run these applications, the required datasets are automatically downladed for you. If you prefer to download them maunally, then please refer to <http://yann.lecun.com/exdb/mnist/> and <https://blog.keras.io/using-pre-trained-word-embeddings-in-a-keras-model.html> for the mnist and news20 applications, respectivally.
```
./run-pipetune.sh
```

Now, if you want to define your own workload and set of hyperparameters then you have to create a `pipetune.conf` file as described bellow and run it as follows:
```Shell
$ python3 pipetune.py --config pipetune.conf
```

The `pipetune.conf` consists of the following 3 main sections:
- `bigdlConf` pointing to the BigDL config file created earlier 
- `powerMeter` defined which power meter you have configured (currently suppports `pdu` and `pcm`)
- `nodes` list of nodes consisting your cluster (spark slave nodes)
- `systemParameters` describing the system parameters to be tuned and the list of values which each parameter can assume
- `hyperParameters` describing the hyper parameters to be tuned and the list of values which each parameter can assume


Below is an example of how this configuration file looks like.
```yaml
{
    "bigdlConf": "bigdl/config/mnist.json",
    "powerMeter": "pcm",
    "nodes": ["slavenode1", "slavenode2", "slavenode3"],
    "systemParameters":
    {
        "cores": ["16", "8", "4"],
        "memory": ["8", "4"]
    },
    "hyperParameters":
    {
        "batch_size": [1024, 512, 32, 64],
        "learning_rate": [0.001, 0.01, 0.1],
        "learning_rate_decay": [0.002, 0.02, 0.2]
    }
}
```

## Paper

[MIDDLEWARE'20] "[PipeTune: Pipeline Parallelism of Hyper and System Parameters Tuning for Deep Learning Clusters
](https://dl.acm.org/doi/10.1145/3423211.3425692)". Isabelly Rocha, Nathaniel Morris, Lydia Y. Chen, Pascal Felber, Robert Birke, Valerio Schiavoni. 

```
@inproceedings{DBLP:conf/middleware/RochaMCFBS20,
  author    = {Isabelly Rocha and
               Nathaniel Morris and
               Lydia Y. Chen and
               Pascal Felber and
               Robert Birke and
               Valerio Schiavoni},
  editor    = {Dilma Da Silva and
               R{\"{u}}diger Kapitza},
  title     = {PipeTune: Pipeline Parallelism of Hyper and System Parameters Tuning
               for Deep Learning Clusters},
  booktitle = {Middleware '20: 21st International Middleware Conference, Delft, The
               Netherlands, December 7-11, 2020},
  pages     = {89--104},
  publisher = {{ACM}},
  year      = {2020},
  url       = {https://doi.org/10.1145/3423211.3425692},
  doi       = {10.1145/3423211.3425692},
  timestamp = {Tue, 15 Dec 2020 14:30:24 +0100},
  biburl    = {https://dblp.org/rec/conf/middleware/RochaMCFBS20.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
