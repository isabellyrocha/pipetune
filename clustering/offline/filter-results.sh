#!/bin/bash

python3 filter_spark_logs.py > data/spark_filtered.log
scp eiger-2.maas:perf/* data/perf
python3 filter_perf_logs.py > data/perf_filtered.log
python3 agg_per_epoch.py > data/agg_per_epoch.log
python3 agg_per_event.py > data/agg_per_event.log
