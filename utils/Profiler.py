from influxdb import InfluxDBClient
from numpy import mean
from pandas import DataFrame
import subprocess
from paramiko import SSHClient
from scp import SCPClient

class Profiler():

    def __init__(self):
#        self.influx_client = InfluxDBClient(args.influx_host, args.influx_port, args.influx_user, args.influx_pass, args.influx_database)
        self.influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'profiler')

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

    def startMeasuring(self, file_name):
        #file_name = "lenet_%s_%s_%s_%s_%d" % (dataset, total_executor_cores, memory, batch_size, trial_id)
        return subprocess.Popen(["ssh", "eiger-2.maas", "./start-perf.sh", file_name])

    def stopMeasuring(self):
        return subprocess.Popen(["ssh", "eiger-2.maas", "./stop-perf.sh"])

    def getMetrics(self, file_name):
        copy = subprocess.Popen("scp eiger-2.maas:perf/%s.stat /home/ubuntu/perf_off" % file_name, shell=True)
        copy.wait()
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect('eiger-2.maas')
        with SCPClient(ssh.get_transport()) as scp:
#    scp.put('test.txt', 'test2.txt')
            try:
                remote = '/home/ubuntu/perf/%s.stat' % file_name
                scp.get(remote, '/home/ubuntu/perf_off')
            except Exception:
                print("Error!")
            finally:
                scp.close()

        #stdout = copy.communicate()[0]
        #print('STDOUT: %s' % stdout)
        events = {}
        with open('/home/ubuntu/perf_off/%s.stat' % file_name) as fp:
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()
            while line:
                sline = line.strip().split(";")
                event = sline[3]
                count = sline[1]
                if "not" in count:
                    count = 0
                if event not in events:
                    events[event] = []
                events[event].append(int(count))
                line = fp.readline()
        events_avg = {}
        for event in events:
            #avg = mean(events[event])
            events_avg[event] = [mean(events[event])]
        return DataFrame(events_avg,columns=list(events_avg.keys()))

