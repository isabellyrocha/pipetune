import subprocess
import time
from datetime import datetime
import json
import os
import sys

def str_to_tstp(time_str:str):
    return int(time.mktime(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timetuple()))

def timestamp():
    return int(datetime.timestamp(datetime.now()))#datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def read_json(file_path:str):
    with open(file_path, 'r') as json_file:
        json_obj = json.load(json_file)
    return json_obj

def next_line(file_name):
    line = file_name.readline()
    while not line:
        line = file_name.readline()
    return line

def setCores(cores):
    command = "ps -aux -a | grep executor | awk '{print $2}' | while read line ; do sudo taskset -cp -pa 0-%d $line  ; done" % (cores-1)
    for node in ["eiger-2.maas"]:
        subprocess.Popen(["ssh", node, command], shell=False ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Changed number of cores to %d... " % cores)

def isEpoch(line, epoch):
    return ("Epoch %d" % epoch) in line

def monitor(file_name):
    epochs = {1:1, 2:2, 3:4}
    cores = 1
    duration = sys.maxsize
 #   file_path = open(file_name, 'r')
    line = next_line(file_name)
    while line:
        if isEpoch(line, 4):
            setCores(cores)
            break
        for epoch in epochs.keys():
            if isEpoch(line, epoch):
                start = timestamp()
                setCores(epochs[epoch])
                finish = timestamp()
                epoch_duration = finish - start
                if epoch_duration < duration:
                    duration = epoch_duration
                    cores = epochs[epoch]
    

def monitor_v1(file_name):
    line = next_line(file_name)
    while line:
        if isEpoch(line, 1):
            start = timestamp()
            setCores(1)
            while isEpoch(line, 1):
                line = next_line(file_name)
            finish = timestamp()
            duration = finish - start
            cores = 1
        elif isEpoch(line, 2):
            start = timestamp()
            setCores(2)
            while isEpoch(line, 2):
                line = next_line(file_name)
            finish = timestamp()
            if (finish - start) < duration:
                duration = finish - start
                cores = 2
        elif isEpoch(line, 3):
            start = timestamp()
            setCores(4)
            while isEpoch(line, 3):
                line = next_line(file_name)
            finish = timestamp()
            if (finish - start) < duration:
                duration = finish - start
                cores = 4
        elif isEpoch(line, 4):
            setCores(cores)
            break

def run_script_v2(args, out =subprocess.PIPE, err =subprocess.PIPE):
    app = subprocess.Popen(args, stdout=out, stderr=err)
#    time.sleep(5)
    monitor(out)
    return app

def run_script(args, out =subprocess.PIPE, err =subprocess.PIPE):
    return subprocess.Popen(args, stdout=out, stderr=err)

def start_perf():
    subprocess.Popen(["bash", "/home/ubuntu/rstat/rstat_start.sh", "eiger-2.maas", "eiger-3.maas", "eiger-4.maas", "eiger-5.maas"], shell=False ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_perf_node(node_name):
    subprocess.Popen(["ssh", node_name, "dstat", "-tTcdgilmnprsy", "--aio", "--unix", "--vm", "--fs", "--ipc", "--lock", "--raw", "--socket", "--tcp", "--udp", "--output", "perf.out"], shell=False ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def stop_perf():
    subprocess.Popen(["bash", "/home/ubuntu/rstat/rstat_stop.sh"], shell=False ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
