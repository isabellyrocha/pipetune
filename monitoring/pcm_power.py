#!/usr/bin/python

import sys
from datetime import datetime
from influxdb import InfluxDBClient
import time 

def get_json(nodename, timestamp, power):
    json_body = [{
        "measurement": "pcm_power/node_utilization",
        "tags": {
            "nodename": nodename,
        },
        "time": timestamp,
        "fields": {
            "value": power
        }
    }]
    return json_body

def next(file_name):
    line = file_name.readline()
    while not line:
        line = file_name.readline()
        time.sleep(1)
    return line

#log_file = open("/home/ubuntu/sprinting/monitoring/eiger-2.log", "r")
file_name = sys.argv[1]
log_file = open(file_name, "r")
node = sys.argv[2]
line = next(log_file)

while not line.startswith("Date"):
   line = next(log_file)

sline = line.split(",")
for i in range(len(sline)):
    if sline[i] == "Proc Energy (Joules)":
        eId = i
        break

client = InfluxDBClient('localhost', 8086, 'root', 'root', 'energy')
while True:
    try:
        line = next(log_file)
        print(line)
        sline = line.split(",")
        date = sline[0]
        print(sline[1])
        t = sline[1].split(".")[0]
        dt = datetime.strptime("%s %s" % (date, t), "%Y-%m-%d %H:%M:%S")
        #timestamp = int(datetime.timestamp(dt))
        power = sline[eId]
        json_body = get_json(node, dt, power)
        client.write_points(json_body)
    except Exception:
        print("Exception has occured. Restarting...")
