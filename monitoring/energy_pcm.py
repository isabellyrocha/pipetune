from datetime import datetime
from influxdb import InfluxDBClient

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
    return line

log_file = open("../../pcm/test.log", "r")
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
    line = next(log_file)
    sline = line.split(",")
    date = sline[0]
    time = sline[1].split(".")[0]
    dt = datetime.strptime("%s %s" % (date, time), "%Y-%m-%d %H:%M:%S")
    #timestamp = int(datetime.timestamp(dt))
    power = sline[eId]
    json_body = get_json('eiger-1', dt, power)
    client.write_points(json_body)
