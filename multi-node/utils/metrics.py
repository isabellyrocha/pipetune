from influxdb import InfluxDBClient

def get_json(appname, batch_size, cores, memory, timestamp, duration, accuracy, energy):
    json_body = [{
        "measurement": "pipetune/metrics",
        "tags": {
            "appname": appname,
            "batchsize": batch_size,
            "cores": cores,
            "memory": memory
        },
        "time": timestamp,
        "fields": {
            "accuracy": accuracy,
            "duration": duration,
            "energy": energy
        }
    }]
    return json_body

def write_metrics_influxdb(appname, batch_size, cores, memory, timestamp, duration, accuracy, energy, client):
    json_body = get_json(appname, batch_size, cores, memory, timestamp, duration, accuracy, energy)
    client.write_points(json_body)

def exists_duration(appname, batch_size, cores, memory):
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'pipetune')
    result = client.query('SELECT "duration" '
                'FROM "pipetune/metrics" '
                'WHERE appname =~ /%s/ AND '
                'batchsize =~ /%s/ AND '
                'cores =~ /%s/ AND '
                'memory =~ /%s/ ' % (appname, batch_size, cores, memory))
    print(result.get_points(measurement='pipetune/metrics'))
    l_restult = list(result.get_points(measurement='pipetune/metrics'))
    return len(l_restult) != 0

def query_duration(appname, batch_size, cores, memory):
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'pipetune')
    result = client.query('SELECT "duration" '
                'FROM "pipetune/metrics" '
                'WHERE appname =~ /%s/ AND '
                'batchsize =~ /%s/ AND '
                'cores =~ /%s/ AND '
                'memory =~ /%s/ ' % (appname, batch_size, cores, memory))
    print(result.get_points(measurement='pipetune/metrics'))
    return list(result.get_points(measurement='pipetune/metrics'))[0]['duration']
