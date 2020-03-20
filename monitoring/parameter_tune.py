from datetime import datetime
import time
import subprocess
import psutil
import os
from influxdb import InfluxDBClient
import numpy

def query_data(node_name, start, end):
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'energy')
    result = client.query('SELECT max(value) '
                'FROM "power/node_utilization" '
                'WHERE nodename =~ /%s/ AND '
                '%d000000000 <= time AND '
                'time <= %d000000000 '
                'group by time(1s) fill(previous)' % (node_name, start, end))
    return list(result.get_points(measurement='power/node_utilization'))

def energy(start, end):
    energy = 0
    for node_name in ['eiger-6', 'eiger-2', 'eiger-3', 'eiger-4']:
        points = query_data(node_name, start, end)
        values = []

        last = 0
        for i in range(len(points)):
            value = points[i]['max']
            if not value == None:
                for j in range(last,i):
                    values.append(value)
                last = i
        for i in range(last, len(points)):
            values.append(value)
#        print(values)
        energy += (numpy.trapz(values))
    return energy

def pcm_energy(start, end):
    energy = 0
    for node_name in ['eiger-1']:#, 'eiger-2', 'eiger-3', 'eiger-4']:
        points = query_data(node_name, start, end)
        values = []

        last = 0
        for i in range(len(points)):
            value = points[i]['max']
            if not value == None:
                for j in range(last,i):
                    values.append(value)
                last = i
        for i in range(last, len(points)):
            values.append(value)
        print(values)
        energy += (numpy.trapz(values))
    return energy

def isEpoch(line):
    return ("Epoch " in line)

def isIteration(iteration, line):
    return ("Iteration %d" %iteration in line)

def next(file_name):
    line = file_name.readline()
    while not line:
        line = file_name.readline()
    return line

def setCores(cores):
    command = "ps -aux -a | grep executor | awk '{print $2}' | while read line ; do sudo taskset -cp -pa 0-%d $line  ; done" % (cores-1)
    for node in ["eiger-6.maas", "eiger-2.maas", "eiger-3.maas", "eiger-4.maas"]:
        subprocess.Popen(["ssh", node, command], shell=False ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Changed number of cores to %d... " % cores)

output_file = open("../traces/mnist.log", "w")
application = subprocess.Popen(["bash", "../applications/run-cifar10.sh", "cifar10", "32", "512", "5"], stdout=output_file)

time.sleep(15)
print("Staring application..")

setCores(1)

log_file = open("../traces/mnist.log", "r")
line = next(log_file)

while not isEpoch(line):
    line = next(log_file)

print("Application has started..")

epochStart = []
epochEnd = []
epochID = 1

#iterations lenet
#iterations = 1875 # batch size: 32
#iterations = 469 # batch size: 128
#iterations =  118# batch size: 512

#iterations cifar10
#iterations = 1563 # batch size: 32
iterations = 98 # batch size: 512

while epochID < 5:
    if "[Iteration %d]" % (iterations*(epochID-1)+1) in line:
        date = line.split(" INFO")[0]
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        print("First iteration..")
        start = int(datetime.timestamp(dt))
        epochStart.append(start)
        if epochID == 2:
            setCores(2)
        if epochID == 3:
            setCores(4) #os.system("ps -aux -a | awk '{print $2}' | while read line ; do sudo taskset -cp 0-0 $line ; done")
        if epochID == 4:
            setCores(8) #os.system("ps -aux -a | awk '{print $2}' | while read line ; do sudo taskset -cp 0-0 $line ; done")
    if "[Iteration %d]" % (iterations*epochID) in line:
        if len(epochStart) > len(epochEnd):
            date = line.split(" INFO")[0]
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            print("Last iteration..")
            end = int(datetime.timestamp(dt))
            epochEnd.append(end)
            print(end-start)
            epochID += 1
    #print(line)
    line = next(log_file)

for i in range(4):
    start = epochStart[i]
    end = epochEnd[i]
    print("%d	%d	%d" % (i, (end-start), energy(start,end)))

print("Best option setup. Waiting application to finish..")
application.wait()
