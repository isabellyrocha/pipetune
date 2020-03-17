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
    for node_name in ['eiger-1', 'eiger-2', 'eiger-3', 'eiger-4']:
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

output_file = open("../traces/mnist.log", "w")
application = subprocess.Popen(["bash", "../applications/run-mnist.sh", "mnist", "16", "128", "5"], stdout=output_file)

time.sleep(5)
print("Staring application..")

os.system("ps -aux -a | awk '{print $2}' | while read line ; do sudo taskset -cp -pa 0-3 $line  ; done")

log_file = open("../traces/mnist.log", "r")
line = next(log_file)

while not isEpoch(line):
    line = next(log_file)

print("Application has started..")

epochStart = []
epochEnd = []
epochID = 1
iterations = 469
while epochID < 4:
    if "[Iteration %d]" % (iterations*(epochID-1)+1) in line:
        date = line.split(" INFO")[0]
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        print("First iteration..")
        start = int(datetime.timestamp(dt))
        epochStart.append(start)
        if epochID == 2:
            os.system("ps -aux -a | awk '{print $2}' | while read line ; do sudo taskset -cp -pa 0-1 $line ; done")
#           os.system("sudo taskset -cp 0-1 %d" % application.pid)
            print("Changing number of cores to 2... ")
        if epochID == 3:
            os.system("ps -aux -a | awk '{print $2}' | while read line ; do sudo taskset -cp 0-0 $line ; done")
#            os.system("sudo taskset -cp 0-0 %d" % application.pid)

            print("Changing number of cores to 1... ")
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

for i in range(3):
    start = epochStart[i]
    end = epochEnd[i]
    print("%d	%d	%d" % (i, (end-start), energy(start,end)))


print("Best option setup. Waiting application to finish..")
application.wait()
