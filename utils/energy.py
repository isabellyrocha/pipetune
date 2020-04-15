from influxdb import InfluxDBClient
import numpy

def query_pdu_data(node_name, start, end):
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'energy')
    result = client.query('SELECT max(value) '
                'FROM "pdu_power/node_utilization" '
                'WHERE nodename =~ /%s/ AND '
                '%d000000000 <= time AND '
                'time <= %d000000000 '
                'group by time(1s) fill(previous)' % (node_name, start, end))
    return list(result.get_points(measurement='pdu_power/node_utilization'))

def query_pcm_data(node_name, start, end):
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'energy')
    result = client.query('SELECT value '
                'FROM "pcm_power/node_utilization" '
                'WHERE nodename =~ /%s/ AND '
                '%d000000000 <= time AND '
                'time <= %d000000000' % (node_name, start, end))
    return list(result.get_points(measurement='pcm_power/node_utilization'))

def pdu_energy(start, end):
    energy = 0
    for node_name in ['eiger-2']:
        points = query_pdu_data(node_name, start, end)
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

def pcm_energy(start, end):
    energy = 0
    for node_name in ['eiger-2', 'eiger-3', 'eiger-4', 'eiger-5']:
        points = query_pcm_data(node_name, start, end)
#        print(points)
        values = []

        #last = 0
        for i in range(len(points)):
            value = points[i]['value']
            if not value == None:
                #for j in range(last,i):
                values.append(float(value))
        #        last = i
        #for i in range(last, len(points)):
        #    values.append(value)
#        print(values)
        energy += (numpy.trapz(values))
    return energy
