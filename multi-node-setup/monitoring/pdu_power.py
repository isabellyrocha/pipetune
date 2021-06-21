#!/usr/bin/env python3

# This is a parser for the json metrics returned by the web interface of the Lindy Ipower Control 2x6 XM
# It writes the Voltage, Current, Active Power and Power factor to a CSV file
# usage:
#       ./pdu-parser.py pdu-outputs-power.csv "http://example-pdu.url" 1
#       python3 /home/ubuntu/pipetune/monitoring/pdu-power-parser.py http://pdu-dell-1.cluster.iiun.unine.ch 1
# hit Ctrl-C when you want to stop the capture

import argparse
import time
import json
import urllib.request
import csv
from datetime import datetime
from influxdb import InfluxDBClient

def get_nodename(node_id):
    switcher = {
        0: "",
        1: "",
        2: "eiger-8",
        3: "eiger-9",
        4: "eiger-4",
        5: "eiger-7",
        6: "eiger-6",
        7: "eiger-5",
        8: "eiger-3",
        9: "eiger-2",
        10: "eiger-1",
        11: ""
    }
    return switcher.get(node_id, "Invalid node id!")

def get_json(nodename, timestamp, power):
    json_body = [{
        "measurement": "pdu_power/node_utilization",
        "tags": {
            "nodename": nodename,
        },
        "time": timestamp,
        "fields": {
            "value": power
        }
    }]
    return json_body

def write_outputs_metrics_influxdb(timestamp, metrics_values, client):
    for output_id in range(2,11):
        nodename = get_nodename(output_id)
        power = metrics_values[output_id][4]['v']
        
        json_body = get_json(nodename, timestamp, power)
        print(json_body)
        client.write_points(json_body)    	
 
def main(status_url, frequency):
    print('Starting PDU monitoring...')
    try:
        client = InfluxDBClient('localhost', 8086, 'root', 'root', 'energy')
        while True:
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')	
            response = urllib.request.urlopen(status_url + '/statusjsn.js?components=16384')
            obj = response.readline().decode('utf8')
#            print(obj)
            metrics = json.loads(obj)
            print(metrics)
            write_outputs_metrics_influxdb(timestamp, metrics['sensor_values'][1]['values'], client)
            time.sleep(frequency)
    except KeyboardInterrupt:
        print('PDU monitoring have been interrupted.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="The PDU status URL")
    parser.add_argument("freq", type=int, help="The metrics refresh frequency in seconds")
    args = parser.parse_args()

    main(args.url, args.freq)
