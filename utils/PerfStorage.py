from influxdb import InfluxDBClient


class PerfStorage():

    def __init__(self, args):
        self.influx_client = InfluxDBClient(args.influx_host, args.influx_port, args.influx_user, args.influx_pass, args.influx_database)

    def write_event(self, measurement: str, tags: dict, timestemp, value: int):
        json_body = [
        {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": {
                "value": value
            }
        }
        ]
        self.influx_client.write_points(json_body)
