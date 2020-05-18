#!/bin/bash

python3 filter_spark_logs.py > spark_filtered.log
scp eiger-2.maas:perf/* /home/ubuntu/perf
python3 filter_perf_logs.py > perf_filtered.log

