#!/bin/bash

#sudo perf stat -e cache-references,cpu/el-capacity/,L1-icache-load-misses,dTLB-loads,iTLB-load-misses,branches,cpu/topdown-slots-retired/,msr/smi/,cpu/cache-misses/,dTLB-stores,cpu/tx-abort/,LLC-loads,cpu/tx-start/,cpu/topdown-recovery-bubbles/,dTLB-store-misses,cpu/tx-conflict/,msr/mperf/,branch-loads,node-load-misses,branch-misses,cpu/el-start/,cpu/cpu-cycles/,cpu/topdown-fetch-bubbles/,dTLB-load-misses,cpu/topdown-slots-issued/,L1-dcache-load-misses,cpu/instructions/,cpu/branch-misses/,cpu/tx-commit/,cpu/mem-loads/,LLC-load-misses,cpu/cycles-t/,cpu/cycles-ct/,LLC-store-misses,L1-dcache-stores,cpu/el-conflict/,cpu/branch-instructions/,cpu/mem-stores/,node-store-misses,cpu/tx-capacity/,cpu/el-abort/,cpu/bus-cycles/,cpu/cache-references/,cpu/el-commit/,node-stores,msr/aperf/,msr/tsc/,LLC-stores,msr/pperf/,cpu/topdown-total-slots/,iTLB-loads,node-loads,branch-load-misses,L1-dcache-loads -a -I 1000 -o $1
sudo perf stat -e cache-references,node-stores -a -I 1000 -o $1.stat
